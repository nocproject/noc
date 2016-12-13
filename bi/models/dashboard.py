# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dashboard storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, DateTimeField, ListField,
                                IntField, BinaryField)


class Dashboard(Document):
    meta = {
        "collection": "noc.dashboards",
        "allow_inheritance": False,
        "indexes": [
            "owner", "tags"
        ]
    }

    title = StringField()
    # Username
    owner = StringField()
    #
    description = StringField()
    #
    tags = ListField(StringField())
    # Config format version
    format = IntField(default=1)
    # gzip'ed data
    config = BinaryField()
    #
    created = DateTimeField(default=datetime.datetime.now)
    changed = DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.title
