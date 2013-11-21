## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectLog model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, ObjectIdField, DateTimeField)


class ObjectLog(Document):
    meta = {
        "collection": "noc.objectlog",
        "allow_inheritance": False,
        "indexes": ["object"]
    }

    object = ObjectIdField()
    ts = DateTimeField()
    user = StringField()
    system = StringField()
    managed_object = StringField()
    message = StringField()
