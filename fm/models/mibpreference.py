# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# MIBPreference model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, IntField
# NOC modules
=======
##----------------------------------------------------------------------
## MIBPreference model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, IntField
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.prettyjson import to_json


class MIBPreference(Document):
    meta = {
        "collection": "noc.mibpreferences",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "json_collection": "fm.mibpreferences"
    }
    mib = StringField(required=True, unique=True)
    preference = IntField(required=True, unique=True)  # The less the better
    uuid = UUIDField(binary=True)

    def __unicode__(self):
        return u"%s(%d)" % (self.mib, self.preference)

    def get_json_path(self):
        return "%s.json" % self.mib

    def to_json(self):
        return to_json({
            "mib": self.mib,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "preference": self.preference
        }, order=["mib", "$collection", "uuid", "preference"])
