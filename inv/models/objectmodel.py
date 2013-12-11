## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectModel model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, UUIDField, DictField,
                                ListField, EmbeddedDocumentField,
                                ObjectIdField)
from mongoengine import signals
## NOC modules
from connectiontype import ConnectionType
from connectionrule import ConnectionRule
from unknownmodel import UnknownModel
from vendor import Vendor
from noc.lib.nosql import PlainReferenceField
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path


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
    cross = StringField(required=False)
    protocols = ListField(StringField(), required=False)
    internal_name = StringField(required=False)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.description == other.description and
            self.type.id == other.type.id and
            self.direction == other.direction and
            self.gender == other.gender and
            self.group == other.group and
            self.cross == other.cross and
            self.protocols == other.protocols and
            self.internal_name == other.internal_name
        )

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "description": self.description,
            "type__name": self.type.name,
            "direction": self.direction,
            "gender": self.gender,
        }
        if self.group:
            r["group"] = self.group
        if self.cross:
            r["cross"] = self.cross
        if self.protocols:
            r["protocols"] = self.protocols
        if self.internal_name:
            r["internal_name"] = self.internal_name
        return r


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
    description = StringField()
    vendor = PlainReferenceField(Vendor)
    connection_rule = PlainReferenceField(ConnectionRule, required=False)
    data = DictField()
    connections = ListField(EmbeddedDocumentField(ObjectModelConnection))
    uuid = UUIDField(binary=True)

    def __unicode__(self):
        return self.name

    def get_data(self, interface, key):
        v = self.data.get(interface, {})
        return v.get(key)

    def save(self, *args, **kwargs):
        super(ObjectModel, self).save(*args, **kwargs)
        # Update connection cache
        # @todo: Move to signal
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

    def has_connection(self, name):
        if self.get_model_connection(name) is None:
            # Check twinax virtual connection
            return (self.get_data("twinax", "twinax") and
                    self.get_data("twinax", "alias") == name)
        else:
            return True

    def get_connection_proposals(self, name):
        """
        Return possible connections for connection name
        as (model id, connection name)
        """
        cn = self.get_model_connection(name)
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
            if (c.name == name or (
                    c.internal_name and c.internal_name == name)):
                return c
        return None

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "uuid": self.uuid,
            "description": self.description,
            "vendor__code": self.vendor.code,
            "data": self.data,
            "connections": [c.json_data for c in self.connections]
        }
        if self.connection_rule:
            r["connection_rule__name"] = self.connection_rule.name
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "uuid", "vendor__code",
                              "description",
                              "connection_rule__name"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"


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

    @classmethod
    def rebuild(cls):
        """
        Rebuild cache
        """
        nc = []
        for m in ObjectModel.objects.all():
            for c in m.connections:
                nc += [{
                    "type": c.type.id,
                    "gender": c.gender,
                    "model": m.id,
                    "name": c.name
                }]
        collection = ModelConnectionsCache._get_collection()
        collection.drop()
        if nc:
            collection.insert(nc)


def clear_unknown_models(sender, document, **kwargs):
    """
    Clear unknown part numbers
    """
    if "asset" in document.data:
        part_no = [
            document.data["asset"][k]
            for k in document.data["asset"]
            if k.startswith("part_no") or k.startswith("order_part_no")
        ]
        if part_no:
            vendor = document.vendor
            if isinstance(vendor, basestring):
                vendor = Vendor.objects.get(id=vendor)
            UnknownModel.clear_unknown(vendor.code, part_no)


signals.post_save.connect(clear_unknown_models, sender=ObjectModel)