# ---------------------------------------------------------------------
# ConnectionRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path
from typing import Any, Dict

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, UUIDField, ListField, EmbeddedDocumentField

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.path import safe_json_path
from noc.core.model.decorator import on_delete_check


class Context(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    type = StringField()
    scope = StringField()
    reset_scopes = ListField(StringField())

    def __str__(self):
        return "%s, %s" % (self.type, self.scope)

    def __eq__(self, other):
        return (
            self.type == other.type
            and self.scope == other.scope
            and self.reset_scopes == other.reset_scopes
        )

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"type": self.type, "scope": self.scope, "reset_scopes": self.reset_scopes}


class Rule(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    match_type = StringField()
    match_connection = StringField()
    scope = StringField()
    target_type = StringField()
    target_number = StringField()
    target_connection = StringField()

    def __str__(self):
        return "%s:%s -(%s)-> %s %s:%s" % (
            self.match_type,
            self.match_connection,
            self.scope,
            self.target_type,
            self.target_number,
            self.target_connection,
        )

    def __eq__(self, other):
        return (
            self.match_type == other.match_type
            and self.match_connection == other.match_connection
            and self.scope == other.scope
            and self.target_type == other.target_type
            and self.target_number == other.target_number
            and self.target_connection == other.target_connection
        )

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "match_type": self.match_type,
            "match_connection": self.match_connection,
            "scope": self.scope,
            "target_type": self.target_type,
            "target_number": self.target_number,
            "target_connection": self.target_connection,
        }


@on_delete_check(check=[("inv.ObjectModel", "connection_rule")])
class ConnectionRule(Document):
    """
    Equipment vendor
    """

    meta = {
        "collection": "noc.connectionrules",
        "strict": False,
        "auto_create_index": False,
        "indexes": [],
        "json_collection": "inv.connectionrules",
        "json_unique_fields": ["name", "uuid"],
    }

    name = StringField(unique=True)
    description = StringField()
    context = ListField(EmbeddedDocumentField(Context))
    rules = ListField(EmbeddedDocumentField(Rule))
    uuid = UUIDField(binary=True)

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "context": [c.json_data for c in self.context],
            "rules": [c.json_data for c in self.rules],
        }

    def to_json(self) -> str:
        return to_json(
            self.json_data, order=["name", "$collection", "uuid", "description", "context", "rules"]
        )

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)
