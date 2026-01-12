# ---------------------------------------------------------------------
# MetricRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple, Set, Union, Callable, FrozenSet
from threading import Lock

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    FloatField,
    ListField,
    DictField,
    StringField,
    BooleanField,
    ObjectIdField,
    EmbeddedDocumentListField,
)
from mongoengine.queryset.visitor import Q as m_q
from django.db.models.query_utils import Q as d_q

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.change.decorator import change
from noc.core.cdag.factory.config import NodeItem, GraphConfig
from noc.core.cdag.node.alarm import VarItem
from noc.core.matcher import build_matcher
from noc.main.models.label import Label
from noc.pm.models.metrictype import MetricType
from noc.pm.models.metricaction import MetricAction
from noc.main.models.pool import Pool
from noc.fm.models.alarmclass import AlarmClass
from noc.config import config

id_lock = Lock()
rule_lock = Lock()
rules_lock = Lock()


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    resource_groups = ListField(ObjectIdField())

    def __str__(self):
        r = f"L: [{self.labels}]"
        if self.exclude_labels:
            r += f";EX:{self.exclude_labels}"
        return r

    def clean(self):
        if not self.labels and not self.exclude_labels and not self.resource_groups:
            raise ValueError()

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.exclude_labels:
            r["labels"] = {"$all_ne": list(self.exclude_labels)}
        if self.resource_groups:
            r["service_groups"] = {"$all": list(self.resource_groups)}
        return r

    def get_q(self):
        """Return instance queryset"""
        q = m_q()
        if self.labels:
            q &= m_q(effective_labels__all=self.labels)
        if self.exclude_labels:
            q &= m_q(effective_labels__nin=self.exclude_labels)
        if self.resource_groups:
            q &= m_q(effective_service_groups__all=self.resource_groups)
        return q

    def get_model_q(self):
        """Return model instance query"""
        q = d_q()
        if self.labels:
            q &= d_q(effective_labels__contains=list(self.labels))
        if self.resource_groups:
            q &= d_q(effective_service_groups__contains=[str(g) for g in self.resource_groups])
        return q


class ThresholdConfig(EmbeddedDocument):
    # Open condition
    op = StringField(choices=["<", "<=", ">=", ">"])
    value = FloatField(default=1.0, null=True)
    # Closing condition
    clear_value = FloatField(default=None, null=True)
    # Alarm class
    alarm_class = PlainReferenceField(AlarmClass)
    alarm_labels = ListField(StringField())

    def get_config(self):
        r = {"op": self.op, "value": self.value}
        if self.clear_value:
            r["clear_value"] = self.clear_value
        if self.alarm_class:
            r["alarm_class"] = self.alarm_class.name
        if self.alarm_labels:
            r["alarm_labels"] = list(self.alarm_labels)
        return r


class MetricActionItem(EmbeddedDocument):
    is_active = BooleanField(default=True)
    metric_type: "MetricType" = PlainReferenceField(MetricType)
    metric_action: "MetricAction" = PlainReferenceField(MetricAction)
    metric_action_params: Dict[str, Any] = DictField()
    thresholds: List["ThresholdConfig"] = EmbeddedDocumentListField(ThresholdConfig)

    def __str__(self) -> str:
        if self.metric_action:
            return str(self.metric_action)
        if self.metric_type:
            return str(self.metric_type)
        return ""

    @property
    def action_id(self) -> str:
        if self.metric_action:
            return str(self.metric_action.id)
        if self.metric_type:
            return str(self.metric_type.id)

    def clean(self):
        ma_params = {}
        if not self.metric_action:
            self.metric_action_params = {}
            return
        for param in self.metric_action.params:
            if param.name not in self.metric_action_params:
                continue
            ma_params[param.name] = param.clean_value(self.metric_action_params[param.name])
        self.metric_action_params = ma_params

    def get_config(self, rule_id: str) -> "GraphConfig":
        return GraphConfig(
            nodes=[
                NodeItem(
                    name="alarm",
                    type="threshold",
                    inputs=[{"name": "x", "node": self.metric_type.field_name}],
                    config={
                        "rule_id": str(rule_id),
                        "action_id": str(self.action_id),
                        "reference": "th:{{vars.rule}}:{{vars.threshold}}:{{object}}:"
                        "{{alarm_class}}:{{';'.join(labels)}}",
                        "error_text_template": None,
                        "thresholds": [t.get_config() for t in self.thresholds],
                        "pool": Pool.get_default_fm_pool().name,
                        "vars": [
                            VarItem(name="rule", value=str(rule_id)),
                            VarItem(name="metric", value=str(self.metric_type.name)),
                        ],
                    },
                )
            ]
        )


@change
class MetricRule(Document):
    meta = {
        "collection": "metricrules",
        "strict": False,
        "auto_create_index": False,
    }
    name = StringField(unique=True)
    description = StringField()
    is_active = BooleanField(default=True)
    match: List["Match"] = EmbeddedDocumentListField(Match)
    actions: List["MetricActionItem"] = EmbeddedDocumentListField(MetricActionItem)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _rule_cache = cachetools.TTLCache(100, ttl=30)
    _rules_cache = cachetools.TTLCache(10, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["MetricRule"]:
        return MetricRule.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rule_cache"), lock=lambda _: rule_lock)
    def get_rules_matcher(cls) -> Tuple[Tuple[Tuple[str, str], FrozenSet[str], Callable], ...]:
        """Build matcher based on Profile Match Rules"""
        r = {}
        for rule in MetricRule.objects.filter(is_active=True):
            for a in rule.actions:
                if not a.is_active:
                    continue
                r[str(rule.id), str(a.action_id)] = (
                    frozenset(rule.get_scopes()),
                    rule.get_matcher(),
                )
        return tuple((x, r[x][0], r[x][1]) for x in r)

    def get_matcher(self) -> Optional[Callable]:
        """Build matcher structure"""
        expr = []
        for mr in self.match or []:
            expr.append(mr.get_match_expr())
        if not expr:
            return None
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def get_scopes(self) -> Set[str]:
        """Return used scopes on actions"""
        scopes = set()
        for a in self.actions:
            if not a.metric_type and not a.metric_action:
                continue
            if a.metric_type:
                scopes.add(a.metric_type.scope.table_name)
                continue
            for ci in a.metric_action.compose_inputs:
                scopes.add(ci.metric_type.scope.table_name)
        return scopes

    def iter_changed_datastream(self, changed_fields=None):
        from noc.inv.models.interface import Interface
        from noc.sla.models.slaprobe import SLAProbe
        from noc.inv.models.cpe import CPE
        from noc.inv.models.sensor import Sensor
        from noc.sa.models.managedobject import ManagedObject

        if config.datastream.enable_cfgmetricrules:
            yield "cfgmetricrules", self.id
        if not config.datastream.enable_cfgmetricstarget:
            return
        object_ids = set()
        # components
        mq = m_q()
        dq = d_q()
        scopes = self.get_scopes()
        for match in self.match:
            if match.resource_groups:
                ids = ManagedObject.objects.filter(
                    effective_service_groups__contains=[str(g) for g in match.resource_groups],
                ).values_list("id", flat=True)
                if not ids:
                    continue
                q = m_q(effective_labels__all=list(match.labels), managed_object__in=ids)
            else:
                q = m_q(effective_labels__all=list(match.labels), managed_object__exists=True)
            if "interface" in scopes:
                object_ids |= set(Interface.objects.filter(q).distinct(field="managed_object"))
            if "sensor" in scopes:
                object_ids |= set(Sensor.objects.filter(q).distinct(field="managed_object"))
            dq |= match.get_model_q()
            mq |= match.get_q()

        if "sla" in scopes:
            for bi_id in SLAProbe.objects.filter(mq).distinct(field="bi_id"):
                yield "cfgmetricstarget", f"sla.SLAProbe::{bi_id}"
        scopes -= {"interface", "sensor", "sla"}
        if object_ids:
            dq |= d_q(id__in=list(object_ids))
        if scopes or dq:
            for bi_id in ManagedObject.objects.filter(dq).values_list("bi_id", flat=True):
                yield "cfgmetricstarget", f"sa.ManagedObject::{bi_id}"
        if scopes and mq:
            for bi_id in CPE.objects.filter(mq).distinct(field="bi_id"):
                yield "cfgmetricstarget", f"inv.CPE::{bi_id}"

    @classmethod
    def get_affected_rules(
        cls, ctx: Dict[str, Any], scope: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """Getting rules for ctx"""
        r = []
        for rule_id, scopes, matcher in cls.get_rules_matcher():
            if scope and scope not in scopes:
                continue
            if matcher(ctx):
                r.append(list(rule_id))
        return r

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rules_cache"), lock=lambda _: rules_lock)
    def get_rules(cls) -> Dict[Set[str], List["MetricActionItem"]]:
        r = defaultdict(list)
        for rid, match, actions in MetricRule.objects.filter(is_active=True).scalar(
            "id", "match", "actions"
        ):
            for m in match:
                for a in actions:
                    if not a.is_active:
                        continue
                    r[frozenset(m.labels)].append([rid, a])
        return r

    @classmethod
    def iter_rules_actions(cls, labels) -> Tuple[str, str]:
        """Iter Rules for labels"""
        labels = set(labels)
        rules = cls.get_rules()
        for rlabels, actions in rules.items():
            if rlabels - labels:
                continue
            for rid, a in actions:
                if a.metric_action:
                    yield str(rid), str(a.metric_action.id)
                elif a.metric_type:
                    yield str(rid), str(a.metric_type.id)
