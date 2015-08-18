## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, URLField,
                                UUIDField)
## NOC modules
from noc.lib.prettyjson import to_json
from noc.lib.collection import collection


@collection
class Vendor(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.vendors",
        "allow_inheritance": False,
        "json_collection": "inv.vendors"
    }

    name = StringField(unique=True)
    code = StringField()
    site = URLField(required=False)
    uuid = UUIDField(binary=True)

    def __unicode__(self):
        return self.name

    def to_json(self):
        return to_json({
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "code": self.code,
            "site": self.site,
            "uuid": self.uuid
        }, order=["name", "uuid", "code", "site"])

    def get_json_path(self):
        return "%s.json" % self.code
