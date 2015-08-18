# -*- coding: utf-8 -*-
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
from noc.lib.prettyjson import to_json
from noc.lib.collection import collection


@collection
class MIBPreference(Document):
    meta = {
        "collection": "noc.mibpreferences",
        "allow_inheritance": False,
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
