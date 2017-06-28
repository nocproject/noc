# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MetricType model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, ReferenceField,
                                UUIDField, ObjectIdField)
import cachetools
# NOC Modules
from noc.inv.models.capability import Capability
from noc.main.models.doccategory import category
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json

id_lock = Lock()


@category
class MetricType(Document):
    meta = {
        "collection": "noc.metrictypes",
        "json_collection": "pm.metrictypes"
    }

    name = StringField(unique=True)
    # InfluxDB table name
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    scope = StringField(
        choices=[
            ("o", "Object"),
            ("i", "Interface"),
            ("p", "Probe")
        ]
    )
    # Measure name, like 'kbit/s'
    measure = StringField()
    #
    required_capability = ReferenceField(Capability)
    # If not empty, script returns a list of metrics
    # denoted wiht <vector_tag>=<value> tags
    vector_tag = StringField()
    #
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "scope": self.scope,
            "measure": self.measure,
            "vector_tag": self.vector_tag
        }
        if self.required_capability:
            r["required_capability__name"] = self.required_capability.name
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "$collection",
                              "uuid", "description",
                              "scope", "measure", "vector_tag"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return MetricType.objects.filter(id=id).first()
