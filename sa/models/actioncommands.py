# ----------------------------------------------------------------------
# ActionCommands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path
import re
from typing import Any, Dict, Optional, List, Iterable, Tuple

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    BooleanField,
    IntField,
    EmbeddedDocumentListField,
    DictField,
    ReferenceField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.sa.models.profile import Profile
from noc.core.path import safe_json_path
from noc.core.prettyjson import to_json
from .action import Action, ScopeConfig


class PlatformMatch(EmbeddedDocument):
    platform_re = StringField()
    version_re = StringField()

    def __str__(self):
        return "%s - %s" % (self.platform_re, self.version_re)

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"platform_re": self.platform_re, "version_re": self.version_re}


class ActionCommandsTestCase(EmbeddedDocument):
    meta = {"strict": False}
    output = StringField()
    context = DictField()

    @property
    def json_data(self):
        return {
            "output": self.output,
            "context": self.context,
        }


class Scope(EmbeddedDocument):
    scope = StringField()
    command = StringField()
    enter_scope = BooleanField(default=False)
    exit_command = StringField()

    def __str__(self):
        return f"{self.scope} - {self.command}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"scope": self.scope, "enter_scope": self.enter_scope, "command": self.command}
        if self.exit_command:
            r["exit_command"] = self.exit_command
        return r

    @property
    def config(self) -> ScopeConfig:
        return ScopeConfig(
            name=self.scope,
            value="",
            command=self.command,
            enter=self.enter_scope,
            exit_command=self.exit_command,
        )


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
    profile: "Profile" = PlainReferenceField(Profile)
    # Config Scopes
    config_mode = BooleanField(default=False)
    scopes: List["Scope"] = EmbeddedDocumentListField(Scope)
    match: List[PlatformMatch] = EmbeddedDocumentListField(PlatformMatch)
    commands = StringField()
    preference = IntField(default=1000)
    timeout = IntField(default=60)
    test_cases: List[ActionCommandsTestCase] = EmbeddedDocumentListField(ActionCommandsTestCase)

    def __str__(self):
        return self.name

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)

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
            "scopes": [c.json_data for c in self.scopes],
            "commands": self.commands,
            "preference": self.preference,
            "timeout": self.timeout,
            "test_cases": [t.json_data for t in self.test_cases],
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
                "test_cases",
            ],
        )

    def get_scope_configs(self) -> Dict[str, ScopeConfig]:
        """Build local configs for Scope"""
        r = {}
        for sc in self.scopes:
            cfg = sc.config
            r[cfg.name] = cfg
        return r

    def is_match(
        self,
        platform: Optional[str] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> bool:
        if not self.match:
            return True
        for m in self.match:
            if (not m.platform_re or (platform and re.search(m.platform_re, platform))) and (
                not m.version_re or (version and re.search(m.version_re, version))
            ):
                return True
        return False

    def iter_cases(self) -> Iterable[Tuple[str, Dict[str, Any]]]:
        """Iterate over test cases"""
        for tc in self.test_cases:
            yield tc.output, tc.context
