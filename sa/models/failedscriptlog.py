# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FailedScriptLog
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import Document, DateTimeField, StringField,\
    IntField


class FailedScriptLog(Document):
    meta = {
        "collection": "noc.log.sa.failed_scripts",
        "allow_inheritance": False,
        "indexes": [
            "-timestamp",
            {
                "fields": ["expires"],
                "expireAfterSeconds": 0
            }
        ]
    }

    timestamp = DateTimeField()
    managed_object = StringField()
    address = StringField()
    script = StringField()
    error_code = IntField()
    error_text = StringField()
    expires = DateTimeField()

    def __unicode__(self):
        return str(self.id)
