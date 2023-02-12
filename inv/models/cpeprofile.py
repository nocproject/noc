# ----------------------------------------------------------------------
# SensorProfile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import operator
from threading import Lock, RLock
from functools import partial
from dataclasses import dataclass

# Third-party modules
import cachetools
from pymongo import ReadPreference
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    LongField,
    BooleanField,
    ReferenceField,
    EmbeddedDocumentField,
    IntField,
)

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.pm.models.metrictype import MetricType
from noc.wf.models.workflow import Workflow
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


id_lock = Lock()
ips_lock = RLock()


@dataclass
class MetricConfig(object):
    metric_type: MetricType
    is_stored: bool
    interval: int


class MatchRule(EmbeddedDocument):
    dynamic_order = IntField(default=0)
    labels = ListField(StringField())
    handler = StringField()

    def __str__(self):
        return ", ".join(self.labels)


class CPEProfileMetrics(EmbeddedDocument):
    meta = {"strict": False}
    metric_type = ReferenceField(MetricType, required=True)
    # Metric collection settings
    # Send metrics to persistent store
    is_stored = BooleanField(default=True)
    # Interval for collecter metrics
    interval = IntField(default=600, min_value=0)

    def __str__(self):
        return f"{self.metric_type} /({self.is_stored})"


@bi_sync
@Label.model
@on_delete_check(check=[("inv.CPE", "profile")])
class CPEProfile(Document):
    meta = {
        "collection": "cpeprofiles",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "labels",
            "effective_labels",
            "match_rules.labels",
            ("dynamic_classification_policy", "match_rules.labels"),
        ],
    }

    name = StringField(unique=True)
    description = StringField()
    workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "inv.SensorProfile")
    )
    style = ForeignKeyField(Style)
    # Sync CPE with Inventory Object
    sync_asset = BooleanField(default=False)
    # Sync CPE with ManagedObject
    sync_managedobject = BooleanField(default=False)
    object_profile = ForeignKeyField(ManagedObjectProfile, required=False)
    # Sync CPE status
    cpe_status_discovery = StringField(choices=[("E", "Enable"), ("D", "Disable")], default="E")
    # Metrics
    enable_collect = BooleanField(default=False)
    metrics_default_interval = IntField(default=0, min_value=0)
    # Interface profile metrics
    metrics = ListField(EmbeddedDocumentField(CPEProfileMetrics))
    # Dynamic Profile Classification
    dynamic_classification_policy = StringField(
        choices=[("R", "By Rule"), ("D", "Disable")],
        default="R",
    )
    #
    match_rules = ListField(EmbeddedDocumentField(MatchRule))
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # BI ID
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _status_discovery_cache = cachetools.TTLCache(maxsize=10, ttl=120)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Sensor Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> "CPEProfile":
        return CPEProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> "CPEProfile":
        return CPEProfile.objects.filter(bi_id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "CPEProfile":
        sp = CPEProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not sp:
            sp = CPEProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                workflow=Workflow.objects.filter(name=cls.DEFAULT_WORKFLOW_NAME).first(),
            )
            sp.save()
        return sp

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_status_discovery_cache"), lock=lambda _: ips_lock
    )
    def get_with_status_discovery(cls):
        """
        Get list of interface profile ids with status_discovery = True
        :return:
        """
        return list(
            x["_id"]
            for x in CPEProfile._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find({"cpe_status_discovery": {"$ne": "D"}}, {"_id": 1})
        )

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_cpeprofile")

    @classmethod
    def _reset_caches(cls, id):
        try:
            del cls._id_cache[
                str(id),  # Tuple
            ]
        except KeyError:
            pass

    def on_save(self):
        self._reset_caches(self.id)
