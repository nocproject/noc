# ----------------------------------------------------------------------
# SensorProfile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import operator
import re
from threading import Lock
from typing import Optional, Union, Dict, Any, Tuple, List, Callable
from functools import partial

# Third-party modules
import cachetools
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    LongField,
    BooleanField,
    EmbeddedDocumentField,
    ObjectIdField,
    IntField,
)
from mongoengine.queryset.visitor import Q as m_q

# NOC modules
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.pm.models.measurementunits import MeasurementUnits
from noc.pm.models.metrictype import MetricType
from noc.wf.models.workflow import Workflow
from noc.core.change.decorator import change
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.matcher import build_matcher
from noc.core.change.model import ChangeField


id_lock = Lock()


class MatchRule(EmbeddedDocument):
    dynamic_order = IntField(default=0)
    labels = ListField(StringField())
    resource_groups = ListField(ObjectIdField())
    units = PlainReferenceField(MeasurementUnits)
    name_pattern = StringField()

    def __str__(self):
        return ", ".join(self.labels)

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.resource_groups:
            r["service_groups"] = {"$all": list(self.resource_groups)}
        if self.units:
            r["units"] = self.units
        if self.name_pattern:
            r["name"] = {"$regex": self.name_pattern}
        return r

    def get_q(self):
        """Return instance queryset"""
        q = m_q()
        if self.labels:
            q &= m_q(effective_labels_all=self.labels)
        if self.resource_groups:
            q &= m_q(effective_service_groups__all=self.resource_groups)
        if self.units:
            q &= m_q(units=self.units)
        if self.name_pattern:
            q &= m_q(label=re.compile(self.name_pattern))
        return q


@bi_sync
@change
@Label.model
@on_delete_check(check=[("inv.Sensor", "profile")])
class SensorProfile(Document):
    meta = {
        "collection": "sensorprofiles",
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
        Workflow, default=partial(Workflow.get_default_workflow, "inv.Sensor")
    )
    style = ForeignKeyField(Style)
    enable_collect = BooleanField(default=False)
    collect_interval = IntField(default=60)
    # PM Integration
    units = PlainReferenceField(MeasurementUnits)
    metric_type: "MetricType" = PlainReferenceField(MetricType)
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

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Sensor Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["SensorProfile"]:
        return SensorProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["SensorProfile"]:
        return SensorProfile.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "SensorProfile":
        sp = SensorProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not sp:
            sp = SensorProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                workflow=Workflow.objects.filter(name=cls.DEFAULT_WORKFLOW_NAME).first(),
            )
            sp.save()
        return sp

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_sensorprofile")

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
        for mop_id, rules in SensorProfile.objects.filter(
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
