## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Capability model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, UUIDField, ObjectIdField)
## NOC modules
from noc.main.models.doccategory import DocCategory
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path


class Capability(Document):
    meta = {
        "collection": "noc.inv.capabilities",
        "json_collection": "inv.capabilities"
    }
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    type = StringField(choices=["bool", "str", "int", "float"])
    category = ObjectIdField()

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "type": self.type
        }
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "$collection",
                              "uuid", "description", "type"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

##
DocCategory.register(Capability)
