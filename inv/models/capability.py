# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Capability model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import operator
from threading import RLock
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, UUIDField, ObjectIdField)
import cachetools
# NOC modules
from noc.main.models.doccategory import category
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path

id_lock = RLock()


@category
class Capability(Document):
    meta = {
        "collection": "noc.inv.capabilities",
        "json_collection": "inv.capabilities"
    }
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    type = StringField(choices=["bool", "str", "int", "float"])
    # Jinja2 template for managed object's card tags
    card_template = StringField(required=False)
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Capability.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return Capability.objects.filter(name=name).first()

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "type": self.type,
            "card_template": self.card_template
        }
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "$collection",
                              "uuid", "description", "type",
                              "card_template"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
