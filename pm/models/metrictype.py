## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MetricType model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField,
                                UUIDField, ObjectIdField)
## NOC Modules
from noc.main.models.doccategory import category
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
from noc.lib.collection import collection


@collection
@category
class MetricType(Document):
    meta = {
        "collection": "noc.pm.metrictypes",
        "json_collection": "pm.metrictypes"
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    is_vector = BooleanField(default=False)
    measure = StringField(default="")
    category = ObjectIdField()

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description
        }
        if self.is_vector:
            r["is_vector"] = self.is_vector
        if self.measure:
            r["measure"] = self.measure
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "$collection",
                              "uuid", "description",
                              "is_vector", "measure"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
