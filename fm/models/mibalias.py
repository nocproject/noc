# ---------------------------------------------------------------------
# MIBAlias model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField

# NOC modules
from noc.core.prettyjson import to_json


class MIBAlias(Document):
    """
    MIB Aliases
    """

    meta = {
        "collection": "noc.mibaliases",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.mibaliases",
        "json_unique_fields": ["rewrite_mib"],
    }
    rewrite_mib = StringField(unique=True)
    to_mib = StringField()
    uuid = UUIDField(binary=True)

    # Lookup cache
    cache = None

    def __str__(self):
        return "%s -> %s" % (self.rewrite_mib, self.to_mib)

    @classmethod
    def rewrite(cls, name):
        """
        Rewrite OID with alias if any
        """
        if cls.cache is None:
            # Initialize cache
            cls.cache = {a.rewrite_mib: a.to_mib for a in cls.objects.all()}
        # Lookup
        if "::" in name:
            mib, rest = name.split("::", 1)
            return "%s::%s" % (cls.cache.get(mib, mib), rest)
        return cls.cache.get(name, name)

    def get_json_path(self) -> str:
        return "%s.json" % self.rewrite_mib.replace(":", "_")

    def to_json(self) -> str:
        return to_json(
            {
                "$collection": self._meta["json_collection"],
                "rewrite_mib": self.rewrite_mib,
                "to_mib": self.to_mib,
                "uuid": self.uuid,
            },
            order=["$collection", "rewrite_mib", "to_mib", "uuid"],
        )
