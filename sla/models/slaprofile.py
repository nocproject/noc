# ---------------------------------------------------------------------
# SLA Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
from functools import partial
from dataclasses import dataclass
from typing import Optional, Dict, List, Union

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
    LongField,
    IntField,
)
from bson import ObjectId
import cachetools

# NOC modules
from noc.main.models.style import Style
from noc.pm.models.metrictype import MetricType
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow
from noc.config import config

id_lock = Lock()
metrics_lock = Lock()


@dataclass
class MetricConfig(object):
    metric_type: MetricType
    is_stored: bool
    interval: int


class SLAProfileMetrics(EmbeddedDocument):
    meta = {"strict": False}
    metric_type: MetricType = ReferenceField(MetricType, required=True)
    # Metric collection settings
    # Enable during box discovery
    # Send metrics to persistent store
    is_stored = BooleanField(default=True)
    # Threshold processing
    interval = IntField(default=300, min_value=0)


@bi_sync
@on_save
@change
@on_delete_check(check=[("sla.SLAProbe", "profile")])
class SLAProfile(Document):
    """
    SLA profile and settings
    """

    meta = {"collection": "noc.sla_profiles", "strict": False, "auto_create_index": False}
    name = StringField(unique=True)
    description = StringField()
    #
    workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "sla.SLAProfile")
    )
    style = ForeignKeyField(Style, required=False)
    # Agent collected intervale
    collect_interval = IntField(default=120)
    # Test packets Number
    test_packets_num = IntField(default=10, min_value=1, max_value=60000)
    # Object id in BI
    bi_id = LongField(unique=True)
    #
    raise_alarm_to_target = BooleanField(default=True)
    #
    metrics_default_interval = IntField(default=0, min_value=0)
    # Number interval buckets
    metrics_interval_buckets = IntField(default=1, min_value=0)
    # Interface profile metrics
    metrics: List[SLAProfileMetrics] = ListField(EmbeddedDocumentField(SLAProfileMetrics))
    # Labels
    labels = ListField(StringField())

    # Caches
    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _slaprofile_metrics = cachetools.TTLCache(maxsize=1000, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "SLAProbe Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["SLAProfile"]:
        return SLAProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["SLAProfile"]:
        try:
            return SLAProfile.objects.get(name=name)
        except SLAProfile.DoesNotExist:
            return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["SLAProfile"]:
        return SLAProfile.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "SLAProfile":
        sp = SLAProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not sp:
            sp = SLAProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                workflow=Workflow.objects.filter(name=cls.DEFAULT_WORKFLOW_NAME).first(),
            )
            sp.save()
        return sp

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_slaprobe")

    @staticmethod
    def config_from_settings(
        m: "SLAProfileMetrics", profile_interval: Optional[int] = None
    ) -> "MetricConfig":
        """
        Returns MetricConfig from .metrics field
        :param m:
        :param profile_interval:
        :return:
        """
        return MetricConfig(m.metric_type, m.is_stored, m.interval or profile_interval)

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_slaprofile_metrics"), lock=lambda _: metrics_lock
    )
    def get_slaprofile_metrics(cls, p_id: "ObjectId") -> Dict[str, MetricConfig]:
        r = {}
        spr = SLAProfile.get_by_id(p_id)
        if not spr:
            return r
        for m in spr.metrics:
            r[m.metric_type.name] = cls.config_from_settings(m, spr.metrics_default_interval)
        return r

    def iter_changed_datastream(self, changed_fields=None):
        from noc.sla.models.slaprobe import SLAProbe

        if not config.datastream.enable_cfgmetricsources:
            return
        if (
            changed_fields
            and "metrics_default_interval" not in changed_fields
            and "metrics" not in changed_fields
            and "labels" not in changed_fields
        ):
            return
        mos = set()
        for mo, bi_id in SLAProbe.objects.filter(profile=self).scalar("managed_object", "bi_id"):
            if mo and (not changed_fields or "metrics_default_interval" in changed_fields):
                mos.add(mo.bi_id)
            if not changed_fields or "metrics" in changed_fields or "labels" in changed_fields:
                yield "cfgmetricsources", f"sla.SLAProbe::{bi_id}"
        for bi_id in mos:
            yield "cfgmetricsources", f"sa.ManagedObject::{bi_id}"

    def get_metric_discovery_interval(self) -> int:
        r = [m.interval or self.metrics_default_interval for m in self.metrics]
        return min(r) if r else 0

    def on_save(self):
        labels = [ll for ll in self.labels if Label.get_effective_setting(ll, "enable_slaprobe")]
        print("ON Save", labels, self._changed_fields)
        if not labels:
            return
        if not hasattr(self, "_changed_fields") or "labels" in self._changed_fields:
            Label.add_model_labels(
                "sla.SLAProbe",
                labels=labels,
                instance_filters=[("profile", self.id)],
            )
