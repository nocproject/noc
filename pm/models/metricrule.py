# ---------------------------------------------------------------------
# MetricRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    ListField,
    DictField,
    StringField,
    BooleanField,
    EmbeddedDocumentField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .metricaction import MetricAction


class MetricRuleItem(EmbeddedDocument):
    metric_action = PlainReferenceField(MetricAction)
    is_active = BooleanField(default=True)
    config = DictField()

    def __str__(self) -> str:
        return str(self.metric_action)


class MetricRule(Document):
    meta = {
        "collection": "metricrules",
        "strict": False,
        "auto_create_index": False,
    }
    name = StringField()
    description = StringField()
    match_labels = ListField(StringField())
    is_active = BooleanField(default=True)
    items = ListField(EmbeddedDocumentField(MetricRuleItem))

    def __str__(self) -> str:
        return str(id(self))
