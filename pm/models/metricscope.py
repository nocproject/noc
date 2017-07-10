# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MetricScope model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, ListField, EmbeddedDocumentField, UUIDField,
    BooleanField)
import cachetools
# NOC Modules
from noc.lib.prettyjson import to_json

id_lock = Lock()


class KeyField(EmbeddedDocument):
    # Table field name
    field_name = StringField()
    # Model reference, i.e. sa.ManagedObject
    model = StringField()

    def __unicode__(self):
        return self.field_name

    def to_json(self):
        return {
            "field_name": self.field_name,
            "model": self.model
        }


class PathItem(EmbeddedDocument):
    name = StringField()
    is_required = BooleanField()
    # Default value, when empty
    default_value = StringField()

    def __unicode__(self):
        return self.name

    def to_json(self):
        v = {
            "name": self.name,
            "is_required": self.is_required
        }
        if self.default_value:
            v["default_value"] = self.default_value
        return v


class MetricScope(Document):
    meta = {
        "collection": "noc.metricscopes",
        "json_collection": "pm.metricscopes",
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    # Database table name
    table_name = StringField()
    description = StringField(required=False)
    key_fields = ListField(EmbeddedDocumentField(KeyField))
    path = ListField(EmbeddedDocumentField(PathItem))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return MetricScope.objects.filter(id=id).first()

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "table_name": self.table_name,
            "description": self.description,
            "key_fields": [kf.json_data() for kf in self.key_fields],
            "path": [p.json_data() for p in self.path]
        }
        return r

    def to_json(self):
        return to_json(
            self.json_data,
            order=[
                "name", "$collection",
                "uuid", "table_name",
                "description",
                "key_fields", "path"])

    def get_json_path(self):
        return "%s.json" % self.name
