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
from mongoengine.fields import (Document, StringField, BooleanField,
                                UUIDField, ObjectIdField)
## NOC Modules
from noc.main.models.doccategory import DocCategory
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json


class MetricType(Document):
    meta = {
        "collection": "noc.pm.metrictypes",
        "allow_inheritance": False,
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
                       order=["name", "uuid", "description",
                              "is_vector", "measure"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

DocCategory.register(MetricType)
