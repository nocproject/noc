# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interaction Log
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine import document, fields


class InteractionLog(document.Document):
    meta = {
        "collection": "noc.log.sa.interaction",
        "allow_inheritance": False,
        "indexes": [("object", "-timestamp")]
    }

    OP_COMMAND = 0
    OP_LOGIN = 1
    OP_LOGOUT = 2
    OP_REBOOT = 3
    OP_STARTED = 4
    OP_HALTED = 5
    OP_CONFIG_CHANGED = 6

    timestamp = fields.DateTimeField()
    object = fields.IntField()
    user = fields.StringField()
    op = fields.IntField()
    text = fields.StringField()

    def __unicode__(self):
        return str(self.id)
