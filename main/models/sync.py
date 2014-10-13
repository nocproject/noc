## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Sync document
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, BooleanField)
## NOC Modules
from noc.lib.nosql import ForeignKeyField
from noc.main.models import User


class Sync(Document):
    meta = {
        "collection": "noc.sync",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    user = ForeignKeyField(User)
    n_instances = IntField(default=1)

    def __unicode__(self):
        return self.name
