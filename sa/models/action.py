# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import operator
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, List, Tuple, Iterable
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
    ListField,
    ReferenceField,
)

# NOC modules
from noc.core.path import safe_json_path
from noc.core.prettyjson import to_json
from noc.core.model.decorator import on_delete_check
from noc.core.handler import get_handler
from noc.core.mongo.fields import PlainReferenceField
from noc.core.models.valuetype import ValueType, ARRAY_ANNEX
from noc.core.runner.models.jobreq import JobRequest, InputMapping, KVInputMapping
from noc.core.topology.base import TopologyBase
from noc.main.models.handler import Handler


id_lock = threading.Lock()
rx_empty_string = re.compile(r"\n{2,}")


@dataclass
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
    disable_command: Optional[str] = None
    enable_command: Optional[str] = None
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

    def render(
        self,
        ctx: Dict[str, Any],
        scope_prepend: str = " ",
        clean_empty_string: bool = True,
        disable_when_change: bool = False,
        ignore_scope: bool = False,
        cancel_prefix: Optional[str] = None,
    ):
        """
        Args:
            ctx: Context for Render commands
            scope_prepend: Add for commands string within scope
            clean_empty_string: Clean empty strings in commands output (for template)
            disable_when_change:
            ignore_scope: Render commands only, without enter scope context
            cancel_prefix: Prefix for cancel commands. Example - 'no'
        """
        r, exits = [], []
        inputs = {"scope_prefix": [], "scope_prepend": scope_prepend}
        inputs |= ctx
        for s in self.scopes or []:
            if ignore_scope:
                continue
            if not s.command:
                # Append space ?
                continue
            if s.enter:
                r.append(s.command)
            inputs["scope_prefix"] += [s.command]
            if disable_when_change and s.enable_command:
                if s.disable_command:
                    r.append(f"{scope_prepend}{s.disable_command}")
                if s.enable_command:
                    exits.append(f"{scope_prepend}{s.enable_command}")
                elif cancel_prefix:
                    exits.append(f"{cancel_prefix} {s.disable_command}")
            if s.exit_command:
                exits.append(s.exit_command)
        inputs["scope_prefix"] = " ".join(inputs["scope_prefix"])
        loader = jinja2.DictLoader({"tpl": self.commands})
        env = jinja2.Environment(loader=loader)
        template = env.get_template("tpl")
        command = template.render(**inputs)
        if clean_empty_string:
            command = rx_empty_string.sub("\n", command)
        if command:
            r.append(command)
        r += exits
        return r


class ActionSetItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    action: "Action" = PlainReferenceField("sa.Action", required=True)
    execute: str = StringField(
        # Success/Failed ?, from param
        choices=[
            ("D", "Disable"),
            ("E", "Enable"),
            ("R", "Rollback"),
            ("S", "Set"),
        ],
        default="S",
    )
    cancel: bool = BooleanField(default=False)
    params_ctx: List[str] = ListField(StringField())
    # domain: str = StringField()
    domain_scopes: List[str] = ListField(StringField())

    def is_match(self, scopes: List[ScopeConfig]) -> bool:
        if scopes and not self.domain_scopes:
            return False
        if scopes:
            return bool(set(self.domain_scopes).intersection({s.name for s in scopes}))
        return True

    def get_ctx(self, **kwargs) -> Dict[str, Any]:
        """Processed Context"""
        if not self.params_ctx:
            return {}
        r = {}
        for c in self.params_ctx:
            param, *set_params = c.split("::")
            if set_params and param in kwargs:
                r[set_params[0]] = kwargs[param]
        return r

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "action": self.name,
            "execute": self.execute,
            "cancel": self.cancel,
        }
        if self.domain_scopes:
            r["domain_scopes"] = list(self.domain_scopes)
        if self.params_ctx:
            r["params_ctx"] = self.params_ctx
        return r


class ActionParameter(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

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
        ("sa.Action", "action_set.action"),
        ("sa.ReactionRule", "action_command_set.action"),
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
    action_job: str = StringField(default="action_commands")
    # Job, Action cfg job, test SLA/ SLA by separate task
    action_set: List[ActionSetItem] = EmbeddedDocumentListField(ActionSetItem)
    # rollback_policy - disable, cancel, action
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
            "params": [c.json_data for c in self.params],
        }
        if self.handler:
            r["handler__uuid"] = self.handler.uuid
        if self.action_set:
            r["action_set"] = [a.json_data for a in self.action_set]
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

    @classmethod
    def iter_topology(
        cls, topology: TopologyBase, constraints: Optional[Dict[str, Any]] = None
    ) -> Iterable[Tuple[Any, Dict[str, Any], Dict[str, Any]]]:
        """Apply action to topology"""
        ports = {}
        mo_c, c_ports = constraints.get("managed_object"), set()
        for n in topology.G.nodes.values():
            print(n)
            if not mo_c or n["mo"] == mo_c:
                yield n["mo"], [], {}
                c_ports |= {p["id"] for p in n["ports"]}
            for p in n["ports"]:
                ports[p["id"]] = (n["mo"], p["ports"][0])
        # Constraints
        for e in topology.iter_edges():
            if c_ports and not set(e["ports"]).intersection(c_ports):
                continue
            for p in e["ports"]:
                if p not in ports:
                    continue
                mo, ifname = ports[p]
                yield mo, [ScopeConfig(name="interface", value=ifname)], {}

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

    def get_enable_action(self) -> Optional["Action"]:
        """Render Enable commands"""
        for a in self.action_set or []:
            if a.execute == "E":
                return a.action
        return None

    @classmethod
    def render_action_commands(
        cls,
        action: "Action",
        profile,
        match_ctx: Optional[Dict[str, Any]] = None,
        managed_object: Optional[Any] = None,
        ignore_scope: bool = False,
        **kwargs,
    ) -> Tuple[Any, List[str]]:
        """
        # Context Scope
        # If multi x multi - to list
        # if multi x single - render and join context
        # if single x multi - to list
        # if single x single - render
        """
        ac = action.get_commands(profile.id, match_ctx)
        if not ac:
            return None, []
        commands, enable_commands = [], None
        command_scopes = ac.get_scope_configs()
        # Disable block
        if ac.disable_when_change:
            # Render Disable commands
            enable_action = action.get_enable_action()
            # To get_effective_commands
            eac = enable_action.get_commands(profile.id, match_ctx)
            scopes = eac.get_scope_configs()
            if scopes and scopes["ip_sla"].enter:
                _, ec = Action.render_action_commands(
                    enable_action,
                    profile,
                    match_ctx,
                    ignore_scope=True,
                    managed_object=managed_object,
                    **kwargs,
                )
                command_scopes = ac.get_scope_configs(enable_scope_commands=" ".join(ec))
            else:
                _, enable_commands = Action.render_action_commands(
                    enable_action,
                    profile,
                    match_ctx,
                    managed_object=managed_object,
                    **kwargs,
                )
        args, scopes = action.clean_args(
            profile,
            command_scopes=command_scopes,
            managed_object=managed_object,
            **kwargs,
        )
        sa_profile = profile.get_profile()
        r = ActionCommandConfig(
            name=action.name,
            commands=ac.commands,
            scopes=scopes,
        )
        commands += r.render(
            args,
            disable_when_change=ac.disable_when_change,
            ignore_scope=ignore_scope,
            cancel_prefix=sa_profile.command_cancel_prefix,
        )
        # Enable block
        if enable_commands:
            commands += enable_commands
        return ac, commands

    def render_commands(
        self,
        profile,
        match_ctx: Optional[Dict[str, Any]] = None,
        managed_object: Optional[Any] = None,
        ignore_scope: bool = False,
        **kwargs,
    ):
        return Action.render_action_commands(
            self,
            profile,
            match_ctx=match_ctx,
            managed_object=managed_object,
            ignore_scope=ignore_scope,
            **kwargs,
        )

    def execute_handler(self, obj, **kwargs):
        """Execute handler"""
        if not self.handler:
            raise ValueError()
        h = get_handler(self.handler)
        req: Optional[JobRequest] = h(obj, **kwargs)
        req.submit()

    def get_execute_commands(
        self,
        managed_object,
        **kwargs,
    ) -> Tuple[str, Any]:
        """Execute commands"""
        match = managed_object.get_matcher_ctx()
        ac, commands = Action.render_action_commands(
            self,
            managed_object.profile,
            match_ctx=match,
            managed_object=managed_object,
            **kwargs,
        )
        if ac is None:
            return "", None
        # Execute rendered commands
        return "\n".join(commands), ac

    def get_job_request(
        self,
        managed_object: Any,
        dry_run: bool = False,
        username: Optional[str] = None,
        **kwargs,
    ) -> JobRequest:
        """Run Action job"""
        inputs = [InputMapping(name="action", value=self.name)]
        if managed_object:
            inputs += [InputMapping(name="managed_object", value=str(managed_object.id))]
        if kwargs:
            inputs += self.clean_action_args(managed_object, **kwargs)
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
        return req

    def register_audit_command(
        self,
        commands,
        username: Optional[str] = None,
    ):
        """Register run command on Audit"""

    def execute_topology(self, topology: TopologyBase, **kwargs):
        jobs = defaultdict(list)
        for mo, s_ctx, ctx in self.iter_topology(topology):
            ctx |= kwargs
            req = self.get_job_request(mo, **ctx)
            jobs[mo].append(req)
        r = []
        for mo, jobs in jobs.items():
            r.append(
                JobRequest(
                    name=f"run_action{self.name}_by_topology_{mo.id}",
                    description="Run Action commands by name",
                    allow_fail=True,
                    locks=[f"mo-{mo.id}"],
                    jobs=jobs,
                )
            )
        # Job UUID request
        return JobRequest(name=f"run_actions_by_topology_{self.id}", jobs=r)

    @classmethod
    def iter_domain_ctx(
        cls,
        domain: Any,
        managed_object: Optional[Any] = None,
        **kwargs,
    ) -> Iterable[Tuple[Any, List[ScopeConfig], Dict[str, Any]]]:
        """Iterate ove Domain topology context"""
        ctx = kwargs.copy()
        if hasattr(domain, "get_domain_ctx"):
            ctx |= domain.get_domain_ctx()
        # Topology from args - effective topology
        if not hasattr(domain, "get_topology"):
            yield domain, [], {}
            return
        topology = domain.get_topology()
        for mo, scopes, t_ctx in cls.iter_topology(topology, {"managed_object": managed_object}):
            t_ctx |= ctx
            yield mo, scopes, t_ctx

    def get_scope_config(self, name: str) -> Optional["ActionParameter"]:
        """Getting scope config"""
        for p in self.params:
            if p.scope and p.scope == name:
                return p

    def iter_scopes_ctx(self, scopes: List[ScopeConfig]) -> Iterable[Dict[str, Any]]:
        """"""
        for s in scopes:
            p = self.get_scope_config(s.name)
            if not p:
                continue
            # Check is_multi
            if not isinstance(s.value, list):
                values = [s.value]
            else:
                values = s.value
            for value in values:
                yield {s.name: value}

    def iter_action_ctxs(
        self,
        domain: Optional[Any] = None,
        managed_object: Optional[Any] = None,
        **kwargs,
    ) -> Iterable[Tuple["Action", Any, Dict[str, Any]]]:
        """Return action ctx"""
        for mo, d_scopes, d_ctx in self.iter_domain_ctx(
            domain, managed_object=managed_object, **kwargs
        ):
            # Scope Ctx
            d_ctx |= kwargs
            s_ctx, scopes = self.clean_args(mo.profile, **d_ctx)
            scopes += d_scopes
            for aa in self.action_set:
                if aa.execute != "S":
                    # Rollback, Cancel ?
                    continue
                if not aa.is_match(d_scopes):
                    continue
                for a_ctx in aa.action.iter_scopes_ctx(scopes):
                    a_ctx |= aa.get_ctx(**d_ctx)
                    a_ctx |= d_ctx
                    yield aa.action, mo, a_ctx
            yield self, mo, d_ctx

    def run(
        self,
        domain: Optional[Any] = None,
        managed_object: Optional[Any] = None,
        as_job: bool = False,
        dry_run: bool = False,
        username: Optional[str] = None,
        **kwargs,
    ):
        """
        Execute Action with context

        # execute_commands -> render_commands -> get_action
        # get_action_job -> submit
        # execute action -> ctx -> get_action_job
        # iter_topology -> [MO, ctx] -> Union ctx -> execute_commands, get_action_job
        #

        Args:
            domain: Configuration Domain
            managed_object: Execute Device param
            username: User for run
            dry_run: Do not execute on Device
        """
        r = defaultdict(list)
        domain = domain or managed_object
        # Domain Ctx
        ctx = kwargs.copy()
        if hasattr(domain, "get_domain_ctx"):
            ctx |= domain.get_action_ctx()
        for action, mo, a_ctx in self.iter_action_ctxs(
            domain, managed_object=managed_object, **ctx
        ):
            r[mo].append((action, a_ctx))
        # Add Job to Settings
        if as_job:
            # Actions Job
            req = self.get_job_by_actions(r, dry_run=dry_run)
            req.submit()
        else:
            self.execute_actions(r, dry_run=dry_run)

    def rollback(self, **kwargs):
        """Run rollback option"""

    def get_job_by_actions(
        self,
        actions: Dict[Any, List[Tuple["Action", Dict[str, Any]]]],
        dry_run: bool = False,
    ) -> "JobRequest":
        """"""
        action_jobs = []
        for mo, aas in actions.items():
            jobs = []
            for action, ctx in aas:
                req = action.get_job_request(mo, dry_run=dry_run, **ctx)
                jobs.append(req)
            action_jobs.append(
                JobRequest(
                    name=f"run_action{self.name}_by_topology_{mo.id}",
                    description="Run Action commands by name",
                    allow_fail=True,
                    locks=[f"mo-{mo.id}"],
                    jobs=jobs,
                )
            )
        # username
        return JobRequest(name=f"run_actions_by_topology_{self.id}", jobs=action_jobs)

    def execute_actions(
        self,
        actions: Dict[Any, List[Tuple["Action", Dict[str, Any]]]],
        dry_run: bool = False,
        as_job: bool = False,
    ):
        """Execute actions over contexts"""
        # Execute Commands
        for mo, aas in actions.items():
            commands = []
            match = mo.get_matcher_ctx()
            for action, ctx in aas:
                # Improve configure script
                _, c = Action.render_action_commands(
                    action,
                    mo.profile,
                    match,
                    managed_object=mo,
                    **ctx,
                )
                commands += c
            mo.scripts.commands(
                commands=commands,
                config_mode=True,
                dry_run=dry_run,
            )

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
            req = self.get_job_request(obj, dry_run=dry_run, username=username, **kwargs)
            req.submit()
        else:
            commands, cfg = self.get_execute_commands(obj, **kwargs)
            obj.scripts.commands(
                commands=[commands],
                config_mode=cfg.config_mode,
                dry_run=dry_run,
            )

    def clean_action_args(
        self,
        managed_object,
        **kwargs,
    ) -> List[KVInputMapping]:
        """Cleanup action arguments"""
        r = []
        args, _ = self.clean_args(managed_object.profile, managed_object=managed_object, **kwargs)
        for k, v in args.items():
            if isinstance(v, list):
                v = ValueType.convert_from_array(v)
            r.append(KVInputMapping(name=k, value=str(v)))
        return r

    def clean_args(
        self,
        profile,
        command_scopes: Optional[Dict[str, ScopeConfig]] = None,
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
            if isinstance(v, str):
                try:
                    tmpl = jinja2.Template(v)
                    v = tmpl.render(**kwargs)
                except jinja2.exceptions.TemplateError as e:
                    raise ValueError("Parameter '%s', Render Error: %s" % (p.name, e))
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
            # Render Action
            args[str(p.name)] = v
            if not p.scope:
                continue
            # Action Command settings
            ac_scope: Optional[ScopeConfig] = command_scopes.get(p.scope)
            e_commands, d_commands = None, None
            if ac_scope:
                command = command_scopes[p.scope].command or p.scope_command
                if ac_scope.enable_command:
                    e_commands = ac_scope.enable_command
                if ac_scope.disable_command:
                    d_commands = ac_scope.enable_command
            else:
                command = p.scope_command
            # Scopes from commands?
            scopes.append(
                ScopeConfig(
                    name=p.scope,
                    value=v,
                    command=command,
                    exit_command=ac_scope.exit_command if ac_scope else p.scope_exit,
                    enable_command=e_commands or None,
                    disable_command=d_commands or None,
                    enter=ac_scope.enter if ac_scope else bool(command),
                )
            )
        # Render Scope command
        for s in scopes:
            # Enter command
            if s.command:
                tmpl = jinja2.Template(s.command)
                s.command = tmpl.render(**args)
        return args, scopes

    def test(self):
        """"""
        from .actioncommands import ActionCommands

        for ac in ActionCommands.objects.filter(action=self).order_by("preference"):
            for out, ctx in ac.iter_cases():
                ac, commands = Action.render_action_commands(self, ac.profile, {}, **ctx)
                commands = "\n".join(commands)
                if commands == out:
                    print(f"[{ac.name}] OK")
                else:
                    print(f"[{ac.name}] FAIL: Expected: {commands}, Required: {out}")
