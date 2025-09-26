# ----------------------------------------------------------------------
# ActionCommands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from typing import Any, Dict

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    BooleanField,
    ListField,
    IntField,
    EmbeddedDocumentField,
    ReferenceField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .profile import Profile
from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json
from .action import Action


class PlatformMatch(EmbeddedDocument):
    platform_re = StringField()
    version_re = StringField()

    def __str__(self):
        return "%s - %s" % (self.platform_re, self.version_re)

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"platform_re": self.platform_re, "version_re": self.version_re}


class ActionCommands(Document):
    meta = {
        "collection": "noc.actioncommands",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "sa.actioncommands",
        "json_depends_on": ["sa.actions", "sa.profile"],
        "json_unique_fields": ["name"],
    }
    name = StringField(unique=True)
    uuid = UUIDField(unique=True)
    action = ReferenceField(Action)
    description = StringField()
    profile = PlainReferenceField(Profile)
    config_mode = BooleanField(default=False)
    match = ListField(EmbeddedDocumentField(PlatformMatch))
    commands = StringField()
    preference = IntField(default=1000)
    timeout = IntField(default=60)

    def __str__(self):
        return self.name

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "action__name": self.action.name,
            "description": self.description,
            "profile__name": self.profile.name,
            "config_mode": self.config_mode,
            "match": [c.json_data for c in self.match],
            "commands": self.commands,
            "preference": self.preference,
            "timeout": self.timeout,
        }

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "action__name",
                "description",
                "profile__name",
                "config_mode",
                "preference",
                "match",
                "commands",
                "timeout",
            ],
        )
