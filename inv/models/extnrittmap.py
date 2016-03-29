# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Exported managed objects to tt mapping
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, StringField, ReferenceField
## NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.ttsystem import TTSystem


class ExtNRITTMap(Document):
    meta = {
        "collection": "noc.extnrittmap",
        "allow_inheritance": False,
        "indexes": [
            "managed_object"
        ]
    }
    managed_object = IntField()
    tt_system = ReferenceField(TTSystem)
    #
    queue = StringField()
    # Managed object's id in terms of TT system
    remote_id = StringField()
