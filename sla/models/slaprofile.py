# ---------------------------------------------------------------------
# SLA Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
from functools import partial
from dataclasses import dataclass
from typing import Optional, Dict

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
from noc.pm.models.thresholdprofile import ThresholdProfile
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow

id_lock = Lock()
metrics_lock = Lock()


@dataclass
class MetricConfig(object):
    metric_type: MetricType
    enable_box: bool
    enable_periodic: bool
    is_stored: bool
    threshold_profile: Optional[ThresholdProfile]


class SLAProfileMetrics(EmbeddedDocument):
    metric_type = ReferenceField(MetricType, required=True)
    # Metric collection settings
    # Enable during box discovery
    enable_box = BooleanField(default=False)
    # Enable during periodic discovery
    enable_periodic = BooleanField(default=True)
    # Send metrics to persistent store
    is_stored = BooleanField(default=True)
    # Threshold processing
    threshold_profile = ReferenceField(ThresholdProfile)


@bi_sync
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
    # Interface profile metrics
    metrics = ListField(EmbeddedDocumentField(SLAProfileMetrics))
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

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
    def get_by_id(cls, id) -> Optional["SLAProfile"]:
        return SLAProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["SLAProfile"]:
        try:
            return SLAProfile.objects.get(name=name)
        except SLAProfile.DoesNotExist:
            return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["SLAProfile"]:
        return SLAProfile.objects.filter(bi_id=id).first()

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
        return Label.get_effective_setting(label, "enable_slaprofile")

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
            r[m.metric_type.name] = cls.config_from_settings(m)
        return r
