# ---------------------------------------------------------------------
# MetricRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from typing import List, Dict, Any, Optional
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

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.change.decorator import change
from noc.main.models.label import Label
from noc.pm.models.metricaction import MetricAction
from noc.config import config

id_lock = Lock()


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

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid) -> Optional["MetricRule"]:
        return MetricRule.objects.filter(id=oid).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgmetricrules:
            yield "cfgmetricrules", self.id
