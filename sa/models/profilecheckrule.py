# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ProfileCheckRule
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, UUIDField, ObjectIdField,
                                IntField)
## NOC modules
from noc.main.models.doccategory import category
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path


@category
class ProfileCheckRule(Document):
    meta = {
        "collection": "noc.profilecheckrules",
        "allow_inheritance": False,
        "json_collection": "sa.profilecheckrules"
    }

    name = StringField(required=True, unique=True)
    uuid = UUIDField(required=True, unique=True)
    description = StringField()
    # Rule preference, processed from lesser to greater
    preference = IntField(required=True, default=1000)
    # Check method
    method = StringField(required=True, choices=[
        "snmp_v2c_get",
        "http_get",
        "https_get"
    ], default="snmp_v2c_get")
    # Method input parameters, defined by method
    param = StringField()
    #
    match_method = StringField(required=True, choices=[
        "eq",  # Full match
        "contains",  # Contains
        "re"   # regular expression
    ], default="eq")
    #
    value = StringField(required=True)
    #
    action = StringField(required=True, choices=[
        "match",
        "maybe"
    ], default="match")
    # Resulting profile name
    profile = StringField(required=True)
    #
    category = ObjectIdField()

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "preference": self.preference,
            "method": self.method,
            "param": self.param,
            "match_method": self.match_method,
            "value": self.value,
            "action": self.action,
            "profile": self.profile
        }

    def to_json(self):
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "preference",
                "method",
                "param",
                "match_method",
                "value",
                "action",
                "profile"
            ])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
