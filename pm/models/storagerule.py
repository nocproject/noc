## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## StorageRule
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (EmbeddedDocumentField, ListField,
                                StringField, IntField, FloatField)


UNITS = {
    "s": 1,
    "m": 60,
    "h": 60 * 60,
    "d": 24 * 60 * 60,
    "w": 7 * 24 * 60 * 60,
    "y": 365 * 24 * 60 * 60
}

unit_choices = [(x, x) for x in UNITS]


class RetentionRule(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    precision = IntField()
    precision_unit = StringField(default="s", choices=unit_choices)
    duration = IntField()
    duration_unit = StringField(default="s", choices=unit_choices)

    def __unicode__(self):
        return "%s%s:%s%s" % (
            self.precision, self.precision_unit.upper(),
            self.duration, self.duration_unit.upper()
        )

    def get_retention(self):
        """
        Return retention config (precision, points)
        """
        precision = self.precision * UNITS[self.precision_unit]
        points = (self.duration * UNITS[self.duration_unit]) / precision
        return precision, points


class StorageRule(Document):
    meta = {
        "collection": "noc.storagerules",
        "allow_inheritance": False
    }
    name = StringField(unique=True)
    aggregation_method = StringField(
        default="average",
        choices=[
            ("average", "Average"),
            ("sum", "Sum"),
            ("max", "Max"),
            ("min", "Min"),
            ("last", "Last")
        ]
    )
    retentions = ListField(EmbeddedDocumentField(RetentionRule))
    xfilesfactor = FloatField(required=False)

    def __unicode__(self):
        return self.name

    def get_retention(self):
        return [r.get_retention() for r in self.retentions]
