# ---------------------------------------------------------------------
# MetricRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import ListField, DictField, StringField, BooleanField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .metricaction import MetricAction


class MetricRule(Document):
    meta = {
        "collection": "metricrules",
        "strict": False,
        "auto_create_index": False,
    }
    metric_action = PlainReferenceField(MetricAction)
    labels = ListField(StringField())
    is_active = BooleanField(default=True)
    config = DictField()

    def __str__(self) -> str:
        return str(id(self))
