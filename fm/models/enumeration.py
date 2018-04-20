# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Enumeration model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, UUIDField
# Python modules
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json


class Enumeration(Document):
    meta = {
        "collection": "noc.enumerations",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "values": self.values
        }, order=["name", "$collection", "uuid"])
