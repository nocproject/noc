# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object Facts
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, DateTimeField, UUIDField
## NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.lib.nosql import ForeignKeyField


class ObjectFact(Document):
    meta = {
        "collection": "noc.objectfacts",
        "index": ["object"]
    }
    uuid = UUIDField(binary=True, primary_key=True)
    object = ForeignKeyField(ManagedObject)
    cls = StringField()
    label = StringField()
    attrs = DictField()
    introduced = DateTimeField(default=datetime.datetime.now)
    changed = DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.object.name
