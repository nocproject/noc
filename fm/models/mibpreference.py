# ---------------------------------------------------------------------
# MIBPreference model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, IntField

# NOC modules
from noc.core.prettyjson import to_json


class MIBPreference(Document):
    meta = {
        "collection": "noc.mibpreferences",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.mibpreferences",
        "json_unique_fields": ["mib", "uuid"],
    }
    mib = StringField(required=True, unique=True)
    preference = IntField(required=True, unique=True)  # The less the better
    uuid = UUIDField(binary=True)

    def __str__(self):
        return "%s(%d)" % (self.mib, self.preference)

    def get_json_path(self) -> str:
        return "%s.json" % self.mib

    def to_json(self) -> str:
        return to_json(
            {
                "mib": self.mib,
                "$collection": self._meta["json_collection"],
                "uuid": self.uuid,
                "preference": self.preference,
            },
            order=["mib", "$collection", "uuid", "preference"],
        )
