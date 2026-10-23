# ---------------------------------------------------------------------
# Interaction Log
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import DateTimeField, EnumField, IntField, StringField

# NOC modules
from noc.core.models.cfginteractions import Interaction


class InteractionLog(Document):
    meta = {
        "collection": "noc.log.sa.interaction",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("object", "-timestamp"), {"fields": ["expire"], "expireAfterSeconds": 0}],
    }

    timestamp = DateTimeField()
    expire = DateTimeField()
    object = IntField()
    user = StringField()
    op = EnumField(Interaction)
    text = StringField()

    def __str__(self):
        return str(self.id)
