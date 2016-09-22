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
from mongoengine.fields import StringField, DateTimeField, ListField


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
    # gzip'ed data
    config = StringField()
    #
    created = DateTimeField(default=datetime.datetime.now)
    changed = DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.title

