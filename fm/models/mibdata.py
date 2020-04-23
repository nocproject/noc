# ---------------------------------------------------------------------
# MIBData model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, ListField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .mib import MIB


class MIBData(Document):
    meta = {
        "collection": "noc.mibdata",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["oid", "name", "mib", "aliases"],
    }
    mib = PlainReferenceField(MIB)
    oid = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField(required=False)
    syntax = DictField(required=False)
    aliases = ListField(StringField(), default=[])

    def __str__(self):
        return self.name
