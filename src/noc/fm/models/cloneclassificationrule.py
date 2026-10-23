# ---------------------------------------------------------------------
# CloneClassificationRule management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path

# Third-party modules
from mongoengine.document import Document
from mongoengine import fields

# NOC modules
from noc.core.path import safe_json_path
from noc.core.prettyjson import to_json


class CloneClassificationRule(Document):
    """
    Classification rules cloning
    """

    meta = {
        "collection": "noc.cloneclassificationrules",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.cloneclassificationrules",
        "json_depends_on": ["fm.eventclassificationrules"],
    }

    name = fields.StringField(unique=True)
    uuid = fields.UUIDField(binary=True)
    re = fields.StringField(default="^.*$")
    key_re = fields.StringField(default="^.*$")
    value_re = fields.StringField(default="^.*$")
    rewrite_from = fields.StringField()
    rewrite_to = fields.StringField()

    def __str__(self):
        return self.name

    def to_json(self) -> str:
        return to_json(
            {
                "name": self.name,
                "$collection": self._meta["json_collection"],
                "uuid": self.uuid,
                "re": self.re,
                "key_re": self.key_re,
                "value_re": self.value_re,
                "rewrite_from": self.rewrite_from,
                "rewrite_to": self.rewrite_to,
            },
            order=["name", "uuid", "re", "key_re", "value_re", "rewrite_from", "rewrite_to"],
        )

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)
