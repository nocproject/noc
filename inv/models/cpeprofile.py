# ----------------------------------------------------------------------
# CPE Profile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import operator
from threading import Lock, RLock
from typing import Optional, Union, Dict, Any, Tuple, List, Callable
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
    ObjectIdField,
    IntField,
)
from mongoengine.queryset.visitor import Q as m_q

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.stencil import stencil_registry
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.change.model import ChangeField
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.matcher import build_matcher
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.main.models.pool import Pool
from noc.pm.models.metrictype import MetricType
from noc.wf.models.workflow import Workflow
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.config import config


id_lock = Lock()
ips_lock = RLock()
CPE_TYPES = IGetCPE.returns.element.attrs["type"].choices


@dataclass
class MetricConfig(object):
    metric_type: MetricType
    is_stored: bool
    interval: int


class MatchRule(EmbeddedDocument):
    dynamic_order = IntField(default=0, min_value=0)
    labels = ListField(StringField())
    resource_groups = ListField(ObjectIdField())
    type = StringField(choices=[(x, x) for x in CPE_TYPES], required=False)

    def __str__(self):
        return ", ".join(self.labels)

    def clean(self):
        super().clean()
        if not self.resource_groups and not self.labels and not self.type:
            raise ValueError("One of condition must be set")

    def get_q(self):
        """Return instance queryset"""
        q = m_q()
        if self.labels:
            q &= m_q(effective_labels_all=self.labels)
        if self.resource_groups:
            q &= m_q(effective_service_groups__all=self.resource_groups)
        if self.type:
            q &= m_q(type=self.type)
        return q

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.resource_groups:
            r["service_groups"] = {"$all": list(self.resource_groups)}
        if self.type:
            r["type"] = self.type
        # if self.name_patter:
        #     r["name"] = {"$regex": self.name_patter}
        # if self.description_patter:
        #     r["description"] = {"$regex": self.description_patter}
        return r


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
        Workflow, default=partial(Workflow.get_default_workflow, "inv.CPE")
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
        return [
            x["_id"]
            for x in CPEProfile._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find({"cpe_status_discovery": {"$ne": "D"}}, {"_id": 1})
        ]

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

        if not config.datastream.enable_cfgmetricstarget:
            return
        if (
            changed_fields
            and "metrics_default_interval" not in changed_fields
            and "metrics" not in changed_fields
            and "labels" not in changed_fields
        ):
            return
        mos = set()
        for controllers, bi_id in CPE.objects.filter(profile=self).scalar("controllers", "bi_id"):
            if controllers and (not changed_fields or "metrics_default_interval" in changed_fields):
                # Check Active?
                mos.add(controllers[0].managed_object.bi_id)
            if not changed_fields or "metrics" in changed_fields or "labels" in changed_fields:
                yield "cfgmetricstarget", f"inv.CPE::{bi_id}"
        for bi_id in mos:
            yield "cfgmetricstarget", f"sa.ManagedObject::{bi_id}"

    def on_save(self):
        self._reset_caches(self.id)

    def get_metric_discovery_interval(self) -> int:
        r = [m.interval or self.metrics_default_interval for m in self.metrics]
        return min(r) if r else 0

    def get_matcher(self) -> Callable:
        """"""
        expr = []
        for mr in self.match_rules:
            expr.append(mr.get_match_expr())
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def is_match(self, o) -> bool:
        """Local Match rules"""
        matcher = self.get_matcher()
        ctx = o.get_matcher_ctx()
        return matcher(ctx)

    @classmethod
    def get_profiles_matcher(cls) -> Tuple[Tuple[str, Callable], ...]:
        """Build matcher based on Profile Match Rules"""
        r = {}
        for mop_id, rules in CPEProfile.objects.filter(
            dynamic_classification_policy="R",
        ).values_list("id", "match_rules"):
            for mr in rules:
                r[(str(mop_id), mr.dynamic_order)] = build_matcher(mr.get_match_expr())
        return tuple((x[0], r[x]) for x in sorted(r, key=lambda i: i[1]))

    @classmethod
    def get_effective_profile(cls, o) -> Optional["str"]:
        policy = getattr(o, "get_dynamic_classification_policy", None)
        if policy and policy() == "D":
            # Dynamic classification not enabled
            return None
        ctx = o.get_matcher_ctx()
        for profile_id, match in cls.get_profiles_matcher():
            if match(ctx):
                return profile_id
        return None

    def get_instance_affected_query(
        self,
        changes: Optional[List[ChangeField]] = None,
        include_match: bool = False,
    ) -> m_q:
        """Return queryset for instance"""
        q = m_q(profile=self.id)
        if include_match and self.match_rules:
            for mr in self.match_rules:
                q |= mr.get_q()
        return q

    def get_css_class(self) -> Optional[str]:
        return self.style.get_css_class() if self.style else None
