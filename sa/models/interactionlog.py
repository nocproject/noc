# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interaction Log
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine import document, fields


@six.python_2_unicode_compatible
class InteractionLog(document.Document):
    meta = {
        "collection": "noc.log.sa.interaction",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            ("object", "-timestamp"),
            {
                "fields": ["expire"],
                "expireAfterSeconds": 0
            }
        ]
    }

    OP_COMMAND = 0
    OP_LOGIN = 1
    OP_LOGOUT = 2
    OP_REBOOT = 3
    OP_STARTED = 4
    OP_HALTED = 5
    OP_CONFIG_CHANGED = 6

    timestamp = fields.DateTimeField()
    expire = fields.DateTimeField()
    object = fields.IntField()
    user = fields.StringField()
    op = fields.IntField()
    text = fields.StringField()

    def __str__(self):
        return str(self.id)
