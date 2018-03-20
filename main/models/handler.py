# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Approved handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField


class Handler(Document):
    meta = {
        "collection": "handlers",
        "strict": False,
        "auto_create_index": False,
    }

    handler = StringField(primary_key=True)
    name = StringField()
    description = StringField()
    allow_config_filter = BooleanField()
    allow_config_validation = BooleanField()

    def __unicode__(self):
        return self.handler
