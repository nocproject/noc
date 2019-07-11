# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UserState model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField


@six.python_2_unicode_compatible
class UserState(Document):
    meta = {
        "collection": "noc.userstate",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("user_id", "key")],
    }
    user_id = IntField()
    key = StringField()
    value = StringField()

    def __str__(self):
        return "%s: %s" % (self.user_id, self.key)
