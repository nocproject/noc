# ----------------------------------------------------------------------
# Workflow Migration model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any
from pathlib import Path

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
    UUIDField,
)

# NOC modules
from noc.core.path import safe_json_path
from noc.core.prettyjson import to_json
from .state import State


class MigrationItem(EmbeddedDocument):
    from_state = ReferenceField(State)
    to_state = ReferenceField(State)
    is_active = BooleanField()
    description = StringField()

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "from_state__name": self.from_state.name,
            "to_state__name": self.to_state.name,
            "is_active": self.is_active,
            "description": self.description,
        }


class WFMigration(Document):
    meta = {
        "collection": "wfmigrations",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "wf.wfmigrations",
        "json_unique_fields": ["name"],
    }
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    migrations = ListField(EmbeddedDocumentField(MigrationItem))

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "uuid": self.uuid,
            "$collection": self._meta["json_collection"],
        }
        if self.description:
            r["description"] = self.description
        if self.migrations:
            r["migrations"] = [m.json_data for m in self.migrations]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "uuid",
                "$collection",
                "description",
                "migrations",
            ],
        )

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)

    def get_translation_map(self, target_wf):
        """
        Returns from_state -> to_state translation
        :param target_wf: Target workflow
        :return:
        """
        return {
            m.from_state: m.to_state
            for m in self.migrations
            if m.is_active and m.to_state.workflow == target_wf
        }
