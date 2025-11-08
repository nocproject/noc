# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import operator
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, List, Tuple
from pathlib import Path

# Third-party modules
import jinja2
import cachetools
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    IntField,
    BooleanField,
    EnumField,
    EmbeddedDocumentListField,
    ReferenceField,
)

# NOC modules
from noc.core.path import safe_json_path
from noc.core.prettyjson import to_json
from noc.core.model.decorator import on_delete_check
from noc.core.handler import get_handler
from noc.core.models.valuetype import ValueType, ARRAY_ANNEX
from noc.main.models.handler import Handler
from noc.core.runner.models.jobreq import JobRequest, InputMapping, KVInputMapping

id_lock = threading.Lock()


@dataclass(frozen=True)
class ScopeConfig:
    """
    Action Configuration Scope
    Attributes:
        name: Scope name
        value:
    """

    name: str
    value: str
    command: Optional[str] = None
    exit_command: Optional[str] = None
    enter: bool = True


@dataclass
class ActionCommandConfig:
    """
    Config Action for render command
    Attributes:
        name: Action name
        commands: Configuration command template
        scopes:
    """

    name: str
    commands: str
    scopes: Optional[List[ScopeConfig]] = None

    def render(self, ctx: Dict[str, Any], scope_prepend: str = " "):
        r, exits = [], []
        inputs = {"scope_prefix": [], "scope_prepend": scope_prepend}
        inputs |= ctx
        for s in self.scopes or []:
            if not s.command:
                # Append space ?
                continue
            if s.enter:
                r.append(s.command)
            inputs["scope_prefix"] += s.command
            if s.exit_command:
                exits.append(s.exit_command)
        inputs["scope_prefix"] = " ".join(inputs["scope_prefix"])
        loader = jinja2.DictLoader({"tpl": self.commands})
        env = jinja2.Environment(loader=loader)
        template = env.get_template("tpl")
        command = template.render(**inputs)
        if command:
            r.append(command)
        r += exits
        return r


class ActionParameter(EmbeddedDocument):
    name = StringField()
    type: ValueType = EnumField(ValueType, required=True)
    multi = BooleanField(default=False)
    description = StringField()
    is_required = BooleanField(default=True)
    default = StringField()
    scope = StringField(required=False)
    scope_command = StringField()
    scope_exit = StringField()

    def __str__(self):
        return f"{self.name} ({self.type})"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "is_required": self.is_required,
        }
        if self.default is not None:
            r["default"] = self.default
        if self.scope:
            r["scope"] = self.scope
        if self.scope_command:
            r["scope_command"] = self.scope_command
        if self.scope_exit:
            r["scope_exit"] = self.scope_exit
        return r


@on_delete_check(
    check=[
        ("sa.ActionCommands", "action"),
        ("sa.ReactionRule", "action_command"),
        ("fm.DispositionRule", "object_actions.action"),
        ("fm.AlarmDiagnosticConfig", "on_clear_action"),
        ("fm.AlarmDiagnosticConfig", "periodic_action"),
        ("fm.AlarmDiagnosticConfig", "on_raise_action"),
    ]
)
class Action(Document):
    meta = {
        "collection": "noc.actions",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "sa.actions",
    }
    uuid = UUIDField(unique=True)
    name = StringField(unique=True)
    label = StringField()
    description = StringField()
    access_level = IntField(default=15)
    # Optional handler for non-sa actions
    handler: "Handler" = ReferenceField(Handler, required=False)
    # rollback_prefix
    #
    params: List[ActionParameter] = EmbeddedDocumentListField(ActionParameter)

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _name_cache = cachetools.TTLCache(1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Action"]:
        return Action.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Action"]:
        return Action.objects.filter(name=name).first()

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "label": self.label,
            "description": self.description,
            "access_level": self.access_level,
        }
        if self.handler:
            r["handler__uuid"] = self.handler.uuid
        r["params"] = [c.json_data for c in self.params]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "label",
                "description",
                "access_level",
                "handler",
                "params",
            ],
        )

    def get_commands(self, profile: str, ctx: Dict[str, Any]):
        """
        Returns ActionCommands instance or None
        Args:
            profile: Managed Object
            ctx: Match Context
        """
        from .actioncommands import ActionCommands

        for ac in ActionCommands.objects.filter(action=self, profile=profile).order_by(
            "preference"
        ):
            if ac.is_match(**ctx):
                return ac
        return None

    def expand_ex(self, profile, match_ctx: Optional[Dict[str, Any]] = None, **kwargs):
        ctx = match_ctx or {}
        ac = self.get_commands(profile.id, ctx)
        if not ac:
            return None, None
        # Render template
        loader = jinja2.DictLoader({"tpl": ac.commands})
        env = jinja2.Environment(loader=loader)
        template = env.get_template("tpl")
        scopes, env_ctx = self.clean_args(profile, **kwargs)
        return ac, template.render(env_ctx)

    def get_config(
        self,
        profile,
        match_ctx: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ActionCommandConfig:
        """"""

    def render_commands(
        self,
        profile,
        match_ctx: Optional[Dict[str, Any]] = None,
        managed_object: Optional[Any] = None,
        **kwargs,
    ) -> Tuple[Any, List[str]]:
        """
        # Context Scope
        # If multi x multi - to list
        # if multi x single - render and join context
        # if single x multi - to list
        # if single x single - render
        """
        ac = self.get_commands(profile.id, match_ctx)
        if not ac:
            return None, []
        args, scopes = self.clean_args(
            profile,
            command_scopes=ac.get_scope_configs(),
            managed_object=managed_object,
            **kwargs,
        )
        r = ActionCommandConfig(
            name=self.name,
            commands=ac.commands,
            scopes=scopes,
        )
        return ac, r.render(args)

    def execute_handler(self, obj, **kwargs):
        """Execute handler"""
        if not self.handler:
            raise ValueError()
        h = get_handler(self.handler)
        req: Optional[JobRequest] = h(obj, **kwargs)
        req.submit()

    def execute_commands(
        self,
        obj,
        dry_run: bool = False,
        username: Optional[str] = None,
        **kwargs,
    ):
        """Execute commands"""
        match = obj.get_matcher_ctx()
        ac, commands = self.render_commands(
            obj.profile,
            match_ctx=match,
            managed_object=obj,
            **kwargs,
        )
        if ac is None:
            return None
        # Execute rendered commands
        commands = "\n".join(commands)
        return obj.scripts.commands(
            commands=[commands],
            config_mode=ac.config_mode,
            dry_run=dry_run,
        )

    def run_action_job(
        self,
        obj,
        dry_run: bool = False,
        username: Optional[str] = None,
        **kwargs,
    ):
        """Run Action job"""
        inputs = [
            InputMapping(name="managed_object", value=str(obj.id)),
            InputMapping(name="action", value=self.name),
        ]
        if kwargs:
            inputs += self.clean_action_args(obj, **kwargs)
        if dry_run:
            inputs.append(InputMapping(name="dry_run", value="true"))
        req = JobRequest(
            name=f"action_commands_{self.name}",
            description="Run Action commands by name",
            action="action_commands",
            inputs=inputs,
            allow_fail=True,
        )
        if username:
            req.environment = {"username": username}
        req.submit()

    def register_audit_command(
        self,
        commands,
        username: Optional[str] = None,
    ):
        """Register run command on Audit"""

    def execute(
        self,
        obj,
        as_job: bool = False,
        dry_run: bool = False,
        username: Optional[str] = None,
        **kwargs,
    ):
        """Run actions to execute"""
        # self.execute_handler(obj, **kwargs)
        # Process
        if self.handler:
            self.execute_handler(obj, dry_run=dry_run, **kwargs)
        elif as_job:
            self.run_action_job(obj, dry_run=dry_run, username=username, **kwargs)
        else:
            self.execute_commands(obj, dry_run=dry_run, **kwargs)

    def clean_action_args(
        self,
        managed_object,
        **kwargs,
    ) -> List[KVInputMapping]:
        """Cleanup action arguments"""
        r = []
        args, _ = self.clean_args(managed_object.profile, **kwargs)
        for k, v in args.items():
            if isinstance(v, list):
                v = ValueType.convert_from_array(v)
            r.append(KVInputMapping(name=k, value=str(v)))
        return r

    def clean_args(
        self,
        profile,
        command_scopes: Optional[Dict[str, ScopeConfig]] = None,
        managed_object: Optional[Any] = None,
        **kwargs,
    ) -> Tuple[Dict[str, Any], List[ScopeConfig]]:
        args, scopes, command_scopes = {}, [], command_scopes or {}
        for p in self.params:
            # is_multy, to iteration
            if p.name not in kwargs and p.is_required and not p.default:
                raise ValueError("Required parameter '%s' is missed" % p.name)
            v = kwargs.get(p.name, p.default)
            if v is None:
                continue
            if p.type == ValueType.IFACE_NAME:
                # Interface
                try:
                    v = profile.get_profile().convert_interface_name(v)
                except Exception:
                    raise ValueError("Invalid interface name in parameter '%s': '%s'" % (p.name, v))
            elif p.type == ValueType.IP_VRF:
                v = p.type.clean_value(v)
                if not v:
                    raise ValueError("Unknown VRF in parameter '%s': '%s'" % (p.name, v))
            elif isinstance(v, str) and v.startswith(ARRAY_ANNEX):
                v = ValueType.convert_to_array(v[len(ARRAY_ANNEX) :])
            elif p.multi and isinstance(v, list):
                v = [p.type.clean_value(x) for x in v]
            elif p.multi:
                v = [p.type.clean_value(x) for x in ValueType.convert_to_array(str(v))]
            else:
                v = p.type.clean_value(v)
            args[str(p.name)] = v
            if not p.scope:
                continue
            # Action Command settings
            ac_scope = command_scopes.get(p.scope)
            if ac_scope:
                command = command_scopes[p.scope].command or p.scope_command
            else:
                command = p.scope_command
            # Enter command
            if command:
                tmpl = jinja2.Template(command)
                command = tmpl.render(**args)
            # Scopes from commands?
            scopes.append(
                ScopeConfig(
                    name=p.name,
                    value=v,
                    command=command,
                    exit_command=ac_scope.exit_command if ac_scope else p.scope_exit,
                    enter=ac_scope.enter if ac_scope else bool(command),
                )
            )
        return args, scopes

    def test(self):
        """"""
        from .actioncommands import ActionCommands

        for ac in ActionCommands.objects.filter(action=self).order_by("preference"):
            for out, ctx in ac.iter_cases():
                ac, commands = self.render_commands(ac.profile, {}, **ctx)
                commands = "\n".join(commands)
                if commands == out:
                    print(f"[{ac.name}] OK")
                else:
                    print(f"[{ac.name}] FAIL: Expected: {commands}, Required: {out}")
