# ---------------------------------------------------------------------
# MetricRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple, Set
from threading import Lock

# Third-party modules
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    ListField,
    DictField,
    StringField,
    BooleanField,
    EmbeddedDocumentListField,
)
from mongoengine.queryset.visitor import Q as m_q
from django.db.models.query_utils import Q as d_q

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.change.decorator import change
from noc.main.models.label import Label
from noc.pm.models.metricaction import MetricAction
from noc.config import config

id_lock = Lock()
rules_lock = Lock()


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())

    def __str__(self):
        return f'{", ".join(self.labels)}-{", ".join(self.exclude_labels)}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


class MetricActionItem(EmbeddedDocument):
    metric_action: "MetricAction" = PlainReferenceField(MetricAction)
    is_active = BooleanField(default=True)
    metric_action_params: Dict[str, Any] = DictField()

    def __str__(self) -> str:
        return str(self.metric_action)

    def clean(self):
        ma_params = {}
        for param in self.metric_action.params:
            if param.name not in self.metric_action_params:
                continue
            ma_params[param.name] = param.clean_value(self.metric_action_params[param.name])
        self.metric_action_params = ma_params


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
    #
    match: List["Match"] = EmbeddedDocumentListField(Match)
    #
    actions: List["MetricActionItem"] = EmbeddedDocumentListField(MetricActionItem)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _rules_cache = cachetools.TTLCache(10, ttl=180)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid) -> Optional["MetricRule"]:
        return MetricRule.objects.filter(id=oid).first()

    def iter_changed_datastream(self, changed_fields=None):
        from noc.inv.models.interface import Interface
        from noc.sla.models.slaprobe import SLAProbe
        from noc.inv.models.cpe import CPE
        from noc.sa.models.managedobject import ManagedObject

        if config.datastream.enable_cfgmetricrules:
            yield "cfgmetricrules", self.id
        if changed_fields and "match" not in changed_fields:
            return
        ids = []
        scopes = set()
        for a in self.actions:
            for ci in a.metric_action.compose_inputs:
                scopes.add(ci.metric_type.scope.table_name)
        mq = m_q()
        dq = d_q()
        for match in self.match:
            mq |= m_q(effective_labels__all=list(match.labels))
            dq |= d_q(effective_labels__contains=list(match.labels))
        if "interface" in scopes:
            ids = list(Interface.objects.filter(mq).distinct(field="managed_object"))
            scopes.remove("interface")
        if ids:
            dq |= d_q(id__in=ids)
        if scopes or ids:
            for bi_id in ManagedObject.objects.filter(dq).values_list("bi_id", flat=True):
                yield "cfgmetricsources", f"sa.ManagedObject::{bi_id}"
        if scopes:
            for bi_id in CPE.objects.filter(mq).distinct(field="bi_id"):
                yield "cfgmetricsources", f"inv.CPE::{bi_id}"
        if "sla" in scopes:
            for bi_id in SLAProbe.objects.filter(mq).distinct(field="bi_id"):
                yield "cfgmetricsources", f"sla.SLAProbe::{bi_id}"

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
        """

        :param labels: Metric Source
        :return:
        """
        labels = set(labels)
        rules = cls.get_rules()
        for rlabels, actions in rules.items():
            if rlabels - labels:
                continue
            for rid, a in actions:
                yield str(rid), str(a.metric_action.id)
