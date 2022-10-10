# ---------------------------------------------------------------------
# SLA Probe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import datetime
from typing import List, Iterable, Optional
from threading import Lock

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    DateTimeField,
    LongField,
    IntField,
    ReferenceField,
    DictField,
)
import cachetools

# NOC modules
from .slaprofile import SLAProfile
from noc.wf.models.state import State
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes
from noc.sa.models.service import Service
from noc.pm.models.agent import Agent
from noc.main.models.label import Label
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.change.decorator import change
from noc.core.bi.decorator import bi_sync
from noc.core.wf.decorator import workflow
from noc.core.models.cfgmetrics import MetricCollectorConfig, MetricItem
from noc.core.model.sql import SQL
from noc.config import config

PROBE_TYPES = IGetSLAProbes.returns.element.attrs["type"].choices

id_lock = Lock()
_target_cache = cachetools.TTLCache(maxsize=100, ttl=60)


@Label.model
@change
@bi_sync
@workflow
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
    service = ReferenceField(Service)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s: %s" % (self.managed_object.name, self.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["SLAProbe"]:
        return SLAProbe.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["SLAProbe"]:
        return SLAProbe.objects.filter(bi_id=id).first()

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
    def get_target(self):
        address = self.target
        if ":" in address:
            # port
            address, port = self.target.split(":")
        # @todo SubInterface search
        return ManagedObject.objects.filter(
            SQL(f"cast_test_to_inet(address) <<= '{address}/32'")
        ).first()

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

    def iter_collected_metrics(
        self, is_box: bool = False, is_periodic: bool = True
    ) -> Iterable[MetricCollectorConfig]:
        """
        Return metrics setting for colleted by box or periodic
        :param is_box:
        :param is_periodic:
        :return:
        """
        if not self.state.is_productive or not self.managed_object:
            return
        metrics = []
        for metric in self.profile.metrics:
            if (is_box and not metric.enable_box) or (is_periodic and not metric.enable_periodic):
                continue
            metrics += [
                MetricItem(
                    name=metric.metric_type.name,
                    field_name=metric.metric_type.field_name,
                    scope_name=metric.metric_type.scope.table_name,
                    is_stored=metric.is_stored,
                    is_compose=metric.metric_type.is_compose,
                )
            ]
        if not metrics:
            # self.logger.info("SLA metrics are not configured. Skipping")
            return
        labels, hints = [f"noc::sla::name::{self.name}"], [
            f"sla_type::{self.type}",
            f"sla_name::{self.name}",
        ]
        if self.group:
            labels += [f"noc::sla::group::{self.group}"]
            hints += [f"sla_group::{self.group}"]
        yield MetricCollectorConfig(
            collector="sla",
            metrics=tuple(metrics),
            labels=tuple(labels),
            hints=hints,
            sla_probe=self.bi_id,
            service=self.service,
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
        return {
            "type": "sla_probe",
            "bi_id": sla_probe.bi_id,
            "fm_pool": sla_probe.managed_object.get_effective_fm_pool().name,
            "labels": labels,
            "metrics": [
                {"name": mc.metric_type.field_name, "is_stored": mc.is_stored}
                for mc in sla_probe.profile.metrics
            ],
            "items": [],
        }

    @property
    def has_configured_metrics(self) -> bool:
        """
        Check configured collected metrics
        :return:
        """
        config = self.get_metric_config(self)
        return config.get("metrics") or config.get("items")
