## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ConnectionType model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, DictField,
                                ListField)
## NOC modules
from noc.lib.nosql import PlainReferenceField
from noc.lib.prettyjson import to_json


class ConnectionType(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.connectiontypes",
        "allow_inheritance": False,
        "indexes": ["extend", "data", "c_group"]
    }

    name = StringField(unique=True)
    is_builtin = BooleanField(default=False)
    description = StringField()
    # Type extends another type, if not null
    extend = PlainReferenceField("self", required=False)
    # Type has male/female gender
    has_gender = BooleanField(default=True)
    # When has_gender == True:
    #     Can many females be connected to single males,
    multi_connection = BooleanField(default=False)
    # ModelData
    data = DictField(default={})
    # Compatible group
    # Connection compatible with opposite gender of same type
    # and all types having any c_group
    c_group = ListField(StringField())

    def __unicode__(self):
        return self.name

    def to_json(self):
        r = {
            "name": self.name,
            "description": self.description,
            "has_gender": self.has_gender,
            "milti_connection": self.multi_connection,
            "c_group": self.c_group
        }
        return to_json([r], order=["name", "description"])

    def get_effective_data(self):
        """
        Calculate effective data
        :return:
        """
        raise NotImplementedError
