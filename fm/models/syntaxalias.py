# ---------------------------------------------------------------------
# SyntaxAlias model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, DictField

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.path import safe_json_path


class SyntaxAlias(Document):
    meta = {
        "collection": "noc.syntaxaliases",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.syntaxaliases",
        "json_unique_fields": ["name"],
    }
    name = StringField(unique=True, required=True)
    syntax = DictField(required=False)
    uuid = UUIDField(binary=True)
    # Lookup cache
    cache = None

    def __str__(self):
        return self.name

    @classmethod
    def rewrite(cls, name, syntax):
        if cls.cache is None:
            cls.cache = {o.name: o.syntax for o in cls.objects.all()}
        return cls.cache.get(name, syntax)

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)

    def to_json(self) -> str:
        return to_json(
            {
                "name": self.name,
                "$collection": self._meta["json_collection"],
                "uuid": self.uuid,
                "syntax": self.syntax,
            },
            order=["name", "$collection", "uuid", "syntax"],
        )
