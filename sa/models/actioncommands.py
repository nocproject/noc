# ----------------------------------------------------------------------
# ActionCommands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
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
from noc.core.models.cfgactioncommands import ActionCommandConfig, ScopeConfig
from noc.sa.models.profile import Profile
from noc.core.text import quote_safe_path
from noc.sa.models.action import Action
from noc.core.prettyjson import to_json


class PlatformMatch(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    platform_re = StringField()
    version_re = StringField()

    def __str__(self):
        return "%s - %s" % (self.platform_re, self.version_re)

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"platform_re": self.platform_re, "version_re": self.version_re}


class ActionCommandsTestCase(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    output = StringField()
    context = DictField()

    @property
    def json_data(self):
        return {
            "output": self.output,
            "context": self.context,
        }


class Scope(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

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
            # exit_command=self.exit_command,
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
    action: "Action" = ReferenceField(Action, required=True)
    description = StringField()
    profile: "Profile" = PlainReferenceField(Profile)
    # Config Scopes
    config_mode = BooleanField(default=False)
    disable_when_change = StringField(
        choices=[
            ("N", "Nothing"),
            ("O", "Out-of-Scope"),
            ("I", "Inner-of-Scope"),
        ],
        default="N",
    )
    scopes: List["Scope"] = EmbeddedDocumentListField(Scope)
    match: List[PlatformMatch] = EmbeddedDocumentListField(PlatformMatch)
    exit_scope_commands = StringField()
    commands = StringField()
    # cancel commands
    # backward_commands
    # cancel_prefix
    preference = IntField(default=1000)
    timeout = IntField(default=60)
    test_cases: List[ActionCommandsTestCase] = EmbeddedDocumentListField(ActionCommandsTestCase)

    def __str__(self):
        return self.name

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "action__name": self.action.name,
            "description": self.description,
            "profile__name": self.profile.name,
            "config_mode": self.config_mode,
            "disable_when_change": self.disable_when_change,
            "match": [c.json_data for c in self.match],
            "scopes": [c.json_data for c in self.scopes],
            "commands": self.commands,
            "preference": self.preference,
            "timeout": self.timeout,
            "test_cases": [t.json_data for t in self.test_cases],
        }
        if self.exit_scope_commands:
            r["exit_scope_commands"] = self.exit_scope_commands
        return r

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
                "disable_when_change",
                "match",
                "commands",
                "timeout",
                "test_cases",
            ],
        )

    def get_config(self, scopes: List[ScopeConfig]) -> "ActionCommandConfig":
        """Get commands config"""
        profile = self.profile.get_profile()
        cfg = self.get_scope_configs()
        r = []
        for s in scopes:
            if s.name in cfg:
                s.update_config(cfg[s.name])
            r.append(s)
        return ActionCommandConfig(
            name=self.action.name,
            commands=self.commands,
            config_mode=self.config_mode,
            cancel_prefix=profile.command_cancel_prefix or None,
            exit_command=self.exit_scope_commands,
            scopes=r,
        )

    def get_scope_configs(self) -> Dict[str, ScopeConfig]:
        """Build local configs for Scope"""
        r = {}
        for sc in self.scopes:
            cfg = sc.config
            r[cfg.name] = cfg
            # Replace to Scope Config
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
