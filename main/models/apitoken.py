# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# APIToken model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField


class APIToken(Document):
    meta = {
        "collection": "apitokens",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            ("type", "user")
        ]
    }

    type = StringField(choices=[
        ("noc-gitlab-api", "NOC Gitlab API")
    ])
    user = IntField()
    token = StringField()

    def __unicode__(self):
        return "%s:%s" % (self.type, self.user)
