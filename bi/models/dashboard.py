# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Dashboard storage
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DateTimeField, ListField,
                                IntField, BinaryField, EmbeddedDocumentField)
# NOC modules
from noc.main.models import User, Group
from noc.lib.nosql import ForeignKeyField

DAL_NONE = -1
DAL_RO = 0
DAL_MODIFY = 1
DAL_ADMIN = 2


class DashboardAccess(EmbeddedDocument):
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)
    level = IntField(choices=[
        (DAL_RO, "Read-only"),
        (DAL_MODIFY, "Modify"),
        (DAL_ADMIN, "Admin")
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

    def get_user_access(self, user):
        # Direct match as owner
        if user == self.owner:
            return DAL_ADMIN
        level = DAL_NONE
        groups = user.groups.all()
        for ar in self.access:
            if ar.user and ar.user == user:
                level = max(level, ar.level)
            if ar.group and ar.group in groups:
                level = max(level, ar.level)
            if level == DAL_ADMIN:
                    return level
        return level
