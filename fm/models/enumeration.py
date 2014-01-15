# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Enumeration model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, UUIDField
## Python modules
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json


class Enumeration(Document):
    meta = {
        "collection": "noc.enumerations",
        "allow_inheritance": False,
        "json_collection": "fm.enumerations"
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    values = DictField()  # value -> [possible combinations]

    def __unicode__(self):
        return self.name

    def get_json_path(self):
        return "%s.json" % quote_safe_path(self.name)

    def to_json(self):
        return to_json({
            "name": self.name,
            "uuid": self.uuid,
            "values": self.values
        }, order=["name", "uuid"])
