# ----------------------------------------------------------------------
# SensorProfile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import operator
from threading import Lock, RLock
from typing import Optional, Union
from functools import partial
from dataclasses import dataclass

# Third-party modules
import bson
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
from noc.core.stencil import stencil_registry
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.main.models.pool import Pool
from noc.pm.models.metrictype import MetricType
from noc.wf.models.workflow import Workflow
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.config import config


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
    interval = IntField(min_value=0)

    def __str__(self):
        return f"{self.metric_type} /({self.is_stored})"


@bi_sync
@change
@Label.model
@on_delete_check(check=[("inv.CPE", "profile")])
class CPEProfile(Document):
    meta = {
        "collection": "cpeprofiles",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "labels",
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
    # Stencils
    shape = StringField(required=False, null=True, choices=stencil_registry.choices, max_length=128)
    shape_title_template = StringField(max_length=256, required=False, null=True)
    # Sync CPE with Inventory Object
    sync_asset = BooleanField(default=False)
    # Sync CPE with ManagedObject
    sync_managedobject = BooleanField(default=False)
    object_profile = ForeignKeyField(ManagedObjectProfile, required=False)
    object_pool = PlainReferenceField(Pool, required=False)
    # Sync CPE status
    cpe_status_discovery = StringField(choices=[("E", "Enable"), ("D", "Disable")], default="E")
    # Metrics
    metrics_default_interval = IntField(default=0, min_value=0)
    # Number interval buckets
    metrics_interval_buckets = IntField(default=1, min_value=0)
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
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["CPEProfile"]:
        return CPEProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["CPEProfile"]:
        return CPEProfile.objects.filter(bi_id=bi_id).first()

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
            del cls._id_cache[str(id),]  # Tuple
        except KeyError:
            pass

    def iter_changed_datastream(self, changed_fields=None):
        from noc.inv.models.cpe import CPE

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
        for mo, bi_id in CPE.objects.filter(profile=self).scalar("controller", "bi_id"):
            if mo and (not changed_fields or "metrics_default_interval" in changed_fields):
                mos.add(mo.bi_id)
            if not changed_fields or "metrics" in changed_fields or "labels" in changed_fields:
                yield "cfgmetricsources", f"inv.CPE::{bi_id}"
        for bi_id in mos:
            yield "cfgmetricsources", f"sa.ManagedObject::{bi_id}"

    def on_save(self):
        self._reset_caches(self.id)

    def get_metric_discovery_interval(self) -> int:
        r = [m.interval or self.metrics_default_interval for m in self.metrics]
        return min(r) if r else 0
