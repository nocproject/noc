# ----------------------------------------------------------------------
# SensorProfile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import operator
import re
from collections import defaultdict
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
from noc.main.models.remotesystem import RemoteSystem
from noc.pm.models.measurementunits import MeasurementUnits
from noc.pm.models.metrictype import MetricType
from noc.wf.models.workflow import Workflow
from noc.core.change.decorator import change
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.matcher import build_matcher
from noc.core.change.model import ChangeField
from noc.config import config


id_lock = Lock()
rule_lock = Lock()
matcher_lock = Lock()


class MatchRule(EmbeddedDocument):
    dynamic_order = IntField(default=0)
    labels = ListField(StringField())
    resource_groups = ListField(ObjectIdField())
    units = PlainReferenceField(MeasurementUnits)
    remote_system = PlainReferenceField(RemoteSystem)
    name_pattern = StringField()

    def __str__(self):
        return ", ".join(self.labels)

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.resource_groups:
            r["service_groups"] = {"$all": list(self.resource_groups)}
        if self.remote_system:
            r["remote_system"] = self.remote_system.id
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
        if self.remote_system:
            q &= m_q(remote_system=self.remote_system.id)
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
    _sensor_profile_matcher = cachetools.TTLCache(maxsize=100, ttl=300)
    _sensor_profile_rules = cachetools.TTLCache(maxsize=10, ttl=300)

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

    def iter_changed_datastream(self, changed_fields=None):
        from noc.inv.models.sensor import Sensor

        if not config.datastream.enable_cfgmetricstarget:
            return
        if (
            changed_fields
            and "enable_collect" not in changed_fields
            and "units" not in changed_fields
        ):
            return
        mos = {
            mo.bi_id
            for mo in Sensor.objects.filter(profile=self, managed_object__exists=True).scalar(
                "managed_object"
            )
        }
        for bi_id in mos:
            yield "cfgmetricstarget", f"sa.ManagedObject::{bi_id}"

    @cachetools.cachedmethod(
        operator.attrgetter("_sensor_profile_matcher"),
        lock=lambda _: matcher_lock,
        key=operator.attrgetter("id"),
    )
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
    @cachetools.cachedmethod(
        operator.attrgetter("_sensor_profile_rules"),
        key=lambda x: "ruleset",
        lock=lambda _: rule_lock,
    )
    def get_profiles_matcher(cls) -> Tuple[Tuple[str, Tuple[Callable, ...]], ...]:
        """Build matcher based on Profile Match Rules"""
        r = defaultdict(list)
        for mop_id, rules in SensorProfile.objects.filter(
            dynamic_classification_policy="R",
        ).values_list("id", "match_rules"):
            for mr in rules:
                r[(str(mop_id), mr.dynamic_order)].append(build_matcher(mr.get_match_expr()))
        return tuple((x[0], tuple(r[x])) for x in sorted(r, key=lambda i: i[1]))

    @classmethod
    def get_effective_profile(cls, o) -> Optional["str"]:
        policy = getattr(o, "get_dynamic_classification_policy", None)
        if policy and policy() == "D":
            # Dynamic classification not enabled
            return None
        ctx = o.get_matcher_ctx()
        for profile_id, matches in cls.get_profiles_matcher():
            for match in matches:
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
