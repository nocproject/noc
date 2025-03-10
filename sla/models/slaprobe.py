# ---------------------------------------------------------------------
# SLA Probe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import operator
import datetime
from typing import List, Iterable, Optional, Dict, Any, Union
from threading import Lock

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    DateTimeField,
    LongField,
    IntField,
    DictField,
)
from pymongo import ReadPreference

# NOC modules
from .slaprofile import SLAProfile
from noc.wf.models.state import State
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes
from noc.pm.models.agent import Agent
from noc.pm.models.metricrule import MetricRule
from noc.main.models.label import Label
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.validators import is_ipv4
from noc.core.change.decorator import change
from noc.core.bi.decorator import bi_sync
from noc.core.wf.decorator import workflow
from noc.core.models.cfgmetrics import MetricCollectorConfig, MetricItem
from noc.core.model.sql import SQL
from noc.core.model.decorator import on_delete_check
from noc.config import config

PROBE_TYPES = IGetSLAProbes.returns.element.attrs["type"].choices

id_lock = Lock()
_target_cache = cachetools.TTLCache(maxsize=100, ttl=60)


@Label.model
@change
@bi_sync
@workflow
@on_delete_check(
    clean=[("sa.Service", "sla_probe")],
)
class SLAProbe(Document):
    meta = {
        "collection": "noc.sla_probes",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["managed_object", "labels", "effective_labels", ("managed_object", "target")],
    }

    managed_object: ManagedObject = ForeignKeyField(ManagedObject)
    agent: Agent = PlainReferenceField(Agent)
    # Probe name (<managed object>, <group>, <name> triple must be unique
    name = StringField()
    # Probe profile
    profile: SLAProfile = PlainReferenceField(SLAProfile, default=SLAProfile.get_default_profile)
    # Probe group (Owner)
    group = StringField()
    # Optional description
    description = StringField()
    state: State = PlainReferenceField(State)
    # Timestamp of last seen
    last_seen = DateTimeField()
    # Timestamp expired
    expired = DateTimeField()
    # Timestamp of first discovery
    first_discovered = DateTimeField(default=datetime.datetime.now)
    # Probe type
    type = StringField(choices=[(x, x) for x in PROBE_TYPES])
    #
    tos = IntField(min=0, max=64)
    # IP address or URL, depending on type
    target = StringField()
    # Hardware timestamps
    hw_timestamp = BooleanField(default=False)
    # Object id in BI
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    extra_labels = DictField()
    #

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s: %s" % (self.managed_object.name, self.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["SLAProbe"]:
        return SLAProbe.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["SLAProbe"]:
        return SLAProbe.objects.filter(bi_id=bi_id).first()

    @property
    def service(self):
        from sa.models.service import Service

        return Service.objects.filter(sla_probe=self).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgmetricsources:
            yield "cfgmetricsources", f"sla.SLAProbe::{self.bi_id}"

    def clean(self):
        if self.extra_labels:
            self.labels += [
                ll
                for ll in Label.merge_labels(self.extra_labels.values())
                if SLAProbe.can_set_label(ll)
            ]

    @cachetools.cached(_target_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_target(self) -> Optional[ManagedObject]:
        from noc.inv.models.subinterface import SubInterface

        address = self.target
        if ":" in address:
            # port
            address, port = self.target.split(":")
        if not is_ipv4(address):
            return
        mo = ManagedObject.objects.filter(SQL(f"address <<= '{address}/32'")).first()
        if mo:
            return mo
        si = SubInterface.objects.filter(ipv4_addresses=re.compile(address)).first()
        if si:
            return si.managed_object

    @classmethod
    def iter_effective_labels(cls, probe: "SLAProbe") -> List[str]:
        return probe.labels + probe.profile.labels

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_slaprobe")

    @classmethod
    def get_component(
        cls, managed_object, sla_probe: str = None, target_address: str = None, **kwargs
    ) -> Optional["SLAProbe"]:
        if not sla_probe or target_address:
            return
        if sla_probe:
            return SLAProbe.get_by_bi_id(int(sla_probe))
        if target_address:
            return SLAProbe.objects.filter(
                managed_object=managed_object, target=target_address
            ).first()

    @classmethod
    def iter_collected_metrics(
        cls, mo, run: int = 0, d_interval: Optional[int] = None
    ) -> Iterable[MetricCollectorConfig]:
        """
        Return metric settings
        :return:
        """
        caps = mo.get_caps()
        sla_count = caps.get("DB | SLAProbes")
        if not sla_count:
            return
        d_interval = d_interval or mo.get_metric_discovery_interval()
        for sla in SLAProbe.objects.filter(managed_object=mo.id).read_preference(
            ReadPreference.SECONDARY_PREFERRED
        ):
            if not sla.state.is_productive:
                continue
            buckets = sla.profile.metrics_interval_buckets
            if not buckets:
                # Auto calculate buckets count
                m_interval = sla.profile.get_metric_discovery_interval()
                buckets = max(1, round(m_interval / d_interval))
            if buckets != 1 and run and sla.bi_id % buckets != run % buckets:
                # Sharder mode, skip inactive shard
                continue
            metrics = []
            for metric in sla.profile.metrics:
                interval = metric.interval or sla.profile.metrics_default_interval or d_interval
                mi = MetricItem(
                    name=metric.metric_type.name,
                    field_name=metric.metric_type.field_name,
                    scope_name=metric.metric_type.scope.table_name,
                    is_stored=metric.is_stored,
                    is_compose=metric.metric_type.is_compose,
                    interval=interval,
                )
                if mi.is_run(d_interval, sla.bi_id, buckets, run):
                    metrics.append(mi)
            if not metrics:
                # self.logger.info("SLA metrics are not configured. Skipping")
                continue
            labels, hints = [f"noc::sla::name::{sla.name}"], [
                f"sla_type::{sla.type}",
                f"sla_name::{sla.name}",
            ]
            if sla.group:
                labels += [f"noc::sla::group::{sla.group}"]
                hints += [f"sla_group::{sla.group}"]
            svc = sla.service
            yield MetricCollectorConfig(
                collector="sla",
                metrics=tuple(metrics),
                labels=tuple(labels),
                hints=hints,
                sla_probe=sla.bi_id,
                service=svc.bi_id if svc else None,
            )

    @classmethod
    def get_metric_config(cls, sla_probe: "SLAProbe"):
        """
        Return MetricConfig for Metrics service
        :param sla_probe:
        :return:
        """
        if not sla_probe.state.is_productive:
            return {}
        labels = []
        for ll in sla_probe.effective_labels:
            l_c = Label.get_by_name(ll)
            labels.append({"label": ll, "expose_metric": l_c.expose_metric if l_c else False})
        source = sla_probe
        if sla_probe.profile.raise_alarm_to_target:
            source = sla_probe.get_target() or source
        return {
            "type": "sla_probe",
            "bi_id": source.bi_id,
            "fm_pool": sla_probe.managed_object.get_effective_fm_pool().name,
            "labels": labels,
            "metrics": [
                {"name": mc.metric_type.field_name, "is_stored": mc.is_stored}
                for mc in sla_probe.profile.metrics
            ],
            "items": [],
            "sharding_key": sla_probe.managed_object.bi_id if sla_probe.managed_object else None,
            "meta": sla_probe.get_message_context(),
            "rules": [ma for ma in MetricRule.iter_rules_actions(sla_probe.effective_labels)],
        }

    @property
    def has_configured_metrics(self) -> bool:
        """
        Check configured collected metrics
        :return:
        """
        config = self.get_metric_config(self)
        return config.get("metrics") or config.get("items")

    @classmethod
    def get_metric_discovery_interval(cls, mo: ManagedObject) -> int:
        coll = cls._get_collection()
        r = coll.aggregate(
            [
                {"$match": {"managed_object": mo.id}},
                {
                    "$lookup": {
                        "from": "slaprofiles",
                        "localField": "profile",
                        "foreignField": "_id",
                        "as": "profiles",
                    }
                },
                {"$unwind": "$profiles"},
                {"$match": {"profiles.metrics": {"$ne": []}}},
                {
                    "$project": {
                        "interval": {
                            "$min": [
                                {"$min": "$profiles.metrics.interval"},
                                "$profiles.metrics_default_interval",
                            ]
                        }
                    }
                },
                {"$group": {"_id": "", "interval": {"$min": "$interval"}}},
            ]
        )
        r = next(r, {})
        return r.get("interval", 0)

    def get_message_context(self) -> Dict[str, Any]:
        r = {"target": self.target, "tos": self.tos}
        if self.managed_object:
            r["source_object"] = self.managed_object.get_message_context()
        target = self.get_target()
        if target:
            r["target_object"] = target.get_message_context()
        if self.service:
            r["service"] = self.service.get_message_context()
        return r
