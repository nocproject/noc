# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Interaction Log
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
##----------------------------------------------------------------------
## Interaction Log
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine import document, fields


class InteractionLog(document.Document):
    meta = {
        "collection": "noc.log.sa.interaction",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

    def __unicode__(self):
        return str(self.id)
