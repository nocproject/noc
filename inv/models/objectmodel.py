## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectModel model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, DictField,
                                ListField, EmbeddedDocumentField)
## NOC modules
from connectiontype import ConnectionType
from vendor import Vendor
from noc.lib.nosql import PlainReferenceField
from noc.lib.prettyjson import to_json


class ObjectModelConnection(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = StringField()
    description = StringField()
    type = PlainReferenceField(ConnectionType)
    direction = StringField(
        choices=[
            "i",  # Inner slot
            "o",  # Outer slot
            "s"   # Connection
        ]
    )
    gender = StringField(choices=["s", "m", "f"])
    group = StringField(required=False)

    def __unicode__(self):
        return self.name


class ObjectModel(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.objectmodels",
        "allow_inheritance": False,
        "indexes": []
    }

    name = StringField(unique=True)
    is_builtin = BooleanField(default=False)
    description = StringField()
    vendor = PlainReferenceField(Vendor)
    data = DictField()
    connections = ListField(EmbeddedDocumentField(ObjectModelConnection))

    def __unicode__(self):
        return self.name

    def to_json(self):
        r = {
            "name": self.name,
            "description": self.description,
            "vendor__name": self.vendor.name,
            "data": self.data,
            "connections": [
                {
                    "name": c.name,
                    "description": c.description,
                    "type__name": c.type.name,
                    "group": c.group,
                    "direction": c.direction,
                    "gender": c.gender
                } for c in self.connections
            ]
        }
        return to_json([r], order=["name", "vendor", "description"])
