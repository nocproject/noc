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
                                ListField, EmbeddedDocumentField,
                                ObjectIdField)
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

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.description == other.description and
            self.type.id == other.type.id and
            self.direction == other.direction and
            self.gender == other.gender and
            self.group == other.group
        )


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

    def save(self, *args, **kwargs):
        super(ObjectModel, self).save(*args, **kwargs)
        # Update connection cache
        s = ObjectModel.objects.filter(id=self.id).first()
        cache = {}
        collection = ModelConnectionsCache._get_collection()
        for cc in ModelConnectionsCache.objects.filter(model=s.id):
            cache[(cc.type, cc.gender, cc.model, cc.name)] = cc.id
        nc = []
        for c in s.connections:
            k = (c.type.id, c.gender, self.id, c.name)
            if k in cache:
                del cache[k]
                continue
            nc += [{
                "type": c.type.id,
                "gender": c.gender,
                "model": self.id,
                "name": c.name
            }]
        if cache:
            for k in cache:
                collection.remove(cache[k])
        if nc:
            collection.insert(nc)

    def get_connection_proposals(self, name):
        """
        Return possible connections for connection name
        as (model id, connection name)
        """
        cn = None
        for c in self.connections:
            if c.name == name:
                cn = c
                break
        if not cn:
            return []  # Connection not found
        r = []
        c_types = cn.type.get_compatible_types(cn.gender)
        og = ConnectionType.OPPOSITE_GENDER[cn.gender]
        for cc in ModelConnectionsCache.objects.filter(
                type__in=c_types, gender=og):
            r += [(cc.model, cc.name)]
        return r

    def get_model_connection(self, name):
        for c in self.connections:
            if c.name == name:
                return c
        return None

    @property
    def json_data(self):
        return {
            "name": self.name,
            "description": self.description,
            "vendor__code": self.vendor.code,
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

    def to_json(self):
        return to_json([self.json_data],
                       order=["name", "vendor__code", "description"])


class ModelConnectionsCache(Document):
    meta = {
        "collection": "noc.inv.objectconnectionscache",
        "allow_inheritance": False,
        "indexes": ["model", ("type", "gender")]
    }
    # Connection type
    type = ObjectIdField()
    gender = StringField(choices=["s", "m", "f"])
    model = ObjectIdField()
    name = StringField()
