# ---------------------------------------------------------------------
# OIDAlias model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.path import safe_json_path


class OIDAlias(Document):
    meta = {
        "collection": "noc.oidaliases",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.oidaliases",
        "json_unique_fields": ["rewrite_oid"],
    }

    rewrite_oid = StringField(unique=True)
    to_oid = StringField()
    description = StringField(required=False)
    uuid = UUIDField(binary=True)

    # Lookup cache
    cache = None

    def __str__(self):
        return "%s -> %s" % (self.rewrite_oid, self.to_oid)

    @classmethod
    def rewrite(cls, oid):
        """
        Rewrite OID with alias if any
        """
        if cls.cache is None:
            # Initialize cache
            cls.cache = {a.rewrite_oid: a.to_oid.split(".") for a in cls.objects.all()}
        # Lookup
        l_oid = oid.split(".")
        rest = []
        while l_oid:
            c_oid = ".".join(l_oid)
            a_oid = cls.cache.get(c_oid)
            if a_oid is not None:
                return ".".join(a_oid + rest)
            rest.insert(0, l_oid.pop())
        # Not found
        return oid

    def get_json_path(self) -> Path:
        return safe_json_path(self.rewrite_oid)

    def to_json(self) -> str:
        r = {
            "rewrite_oid": self.rewrite_oid,
            "to_oid": self.to_oid,
            "uuid": self.uuid,
            "$collection": self._meta["json_collection"],
        }
        if self.description:
            r["description"] = self.description
        return to_json(r, order=["$collection", "rewrite_oid", "to_oid", "uuid"])
