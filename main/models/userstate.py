# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UserState model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField


class UserState(Document):
    meta = {
        "collection": "noc.userstate",
        "allow_inheritance": False,
        "indexes": [
            ("user_id", "key")
        ]
    }
    user_id = IntField()
    key = StringField()
    value = StringField()

    def __unicode__(self):
        return "%s: %s" % (self.user_id, self.key)
