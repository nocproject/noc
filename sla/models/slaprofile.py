# ---------------------------------------------------------------------
# SLA Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
    LongField,
)
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
    workflow = PlainReferenceField(Workflow)
    style = ForeignKeyField(Style, required=False)
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

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "SLAProbe Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return SLAProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        try:
            return SLAProfile.objects.get(name=name)
        except SLAProfile.DoesNotExist:
            return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> "SLAProfile":
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
