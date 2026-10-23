# ----------------------------------------------------------------------
# CHPolicy model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, IntField


class CHPolicy(Document):
    meta = {"collection": "chpolicies", "strict": False, "auto_create_index": False}

    table = StringField(unique=True, required=True)
    is_active = BooleanField(default=True)
    ttl = IntField(default=0, required=True)

    def __str__(self) -> str:
        return self.table
