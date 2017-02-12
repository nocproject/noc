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
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DateTimeField, ListField,
                                IntField, BinaryField, EmbeddedDocumentField)
## NOC modules
from noc.main.models import User, Group
from noc.lib.nosql import ForeignKeyField


class DashboardAccess(EmbeddedDocument):
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)
    level = IntField(choices=[
        (0, "Read-only"),
        (1, "Modify"),
        (2, "Admin")
    ])


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
    owner = ForeignKeyField(User)
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
    #
    access = ListField(EmbeddedDocumentField(DashboardAccess))

    def __unicode__(self):
        return self.title
