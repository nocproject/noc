# ---------------------------------------------------------------------
# Object Event Reaction Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, List, Union, Dict, Any, Callable, Tuple, Iterable
# from pathlib import Path

# Third-party modules
import cachetools
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.queryset.visitor import Q as m_q
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    LongField,
    IntField,
    UUIDField,
    ReferenceField,
    EnumField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.main.models.label import Label
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.capability import Capability
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject
from noc.wf.models.state import State
from noc.core.models.cfgactions import ActionType
from noc.core.matcher import build_matcher
from noc.core.runner.job import JobRequest
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.change.model import ChangeItem
from noc.core.change.policy import REACTION_MODELS
from noc.core.model.decorator import tree, on_delete_check

id_lock = Lock()


class ActionCommands(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    action: Action = ReferenceField(Action)
    allow_fail: bool = BooleanField(default=True)
    clean_action: bool = BooleanField(default=False)
    enable_scope_action = StringField(
        choices=[
            ("N", "Do Nothing"),
            ("E", "Enable"),
            ("D", "Disable"),
            ("A", "Action"),
        ],
        default="A",
    )
    # topology_role
    # run_all: bool = BooleanField()
    # repeat: bool = BooleanField(default=True)
    context = ListField(StringField())

    def __str__(self):
        return f"{self.action}: AF: {self.allow_fail}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "action__name": self.action.name,
            "allow_fail": self.allow_fail,
            "clean_action": self.clean_action,
        }
        if self.context:
            r["context"] = list(self.context)
        return r


class ActionItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    action: ActionType = EnumField(ActionType, required=True)
    run: str = StringField(
        choices=[
            ("A", "Always"),
            ("F", "Commands Set Failed"),
            ("S", "Commands Set Success"),
        ],
        default="A",
    )
    handler: "Handler" = ReferenceField(Handler, required=False)
    wf_event = StringField(required=False)

    def __str__(self):
        return f"C: {self.action}; W: {self.wf_event}; H: {self.handler}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"action": self.action.value, "run": self.run}
        # if self.interaction_audit:
        #    r["interaction_audit"] = self.interaction_audit.value
        if self.handler:
            r["handler__name"] = list(self.handler.name)
        return r

    def get_config(self) -> Dict[str, Any]:
        """Get Action config"""
        key, args = None, {}
        match self.action:
            case ActionType.FIRE_WF_EVENT:
                args = {"wf_event": self.wf_event}
                key = ""
            case ActionType.HANDLER:
                key = self.handler.handler
            case ActionType.RUN_DISCOVERY:
                key = ""
                # if self.interaction_audit:
                #    args = {"audit": self.interaction_audit}
        if key is not None:
            return {"action": self.action.value, "key": key, "cfg": args}
        return {}


class ConfigurationDomain(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    model_id: str = StringField(required=True)
    rule: Optional["ReactionRule"] = PlainReferenceField("sa.ReactionRule", required=False)
    change: str = StringField(default="topology")
    reaction: str = StringField(choices=[("A", "Affected"), ("M", "Match")], default="A")
    suppress_action: bool = BooleanField(default=False)
    ctx: str = StringField(choices=[("D", "Domain"), ("L", "Local")])
    # affected, match
    # Affected_object
    # name: str = StringField(required=False)
    # topology_handler = StringField()


class FieldData(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    field = StringField(required=False)
    capability: Optional[Capability] = ReferenceField(Capability)
    wildcard = ReferenceField(Label, required=False)
    # operations: List[str] = ListField(StringField(
    #     choices=["create", "update", "delete", "topology", "any"], default="any"),
    # )
    condition = StringField(
        choices=[
            "regex",
            "contains",
            "exists",
            "eq",
            "ne",
            "gte",
            "gt",
            "lte",
            "lt",
            "any",
            # Len (for), exists, not_one, add_ctx
        ],
        default="any",
    )
    value = StringField(required=False)
    # Action Context
    set_context = StringField(required=False)

    def __str__(self):
        field = self.field or self.capability
        if self.condition and self.value:
            r = f"{field} {self.condition} {self.value}"
        else:
            r = field
        if self.set_context:
            r = f"{r} (set: {self.set_context})"
        return r

    def clean(self):
        super().clean()
        if not self.field and not self.capability:
            raise ValueError("Field or Caps Must Be set")

    def get_match_expr(self) -> Dict[str, Any]:
        """"""
        if self.capability:
            return {"caps": {"$in": [self.capability.name]}}
        # Field matcher
        if self.condition and self.value:
            return {self.field: {f"${self.condition}": self.value}}
        return {}

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"field": self.field}
        if self.capability:
            r["capability__uuid"] = str(self.capability.uuid)
        if self.condition and self.value:
            r |= {"condition": self.condition, "value": self.value}
        if self.set_context:
            r["set_context"] = self.set_context
        return r


class Match(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    groups: List[ResourceGroup] = ListField(ReferenceField(ResourceGroup, required=True))
    ex_groups: List[ResourceGroup] = ListField(ReferenceField(ResourceGroup, required=True))
    remote_system: Optional["RemoteSystem"] = ReferenceField(RemoteSystem, required=False)
    wf_states: List["State"] = ListField(ReferenceField(State, required=True))

    def clean(self):
        super().clean()
        if not self.groups and not self.labels and not self.remote_system and not self.wf_states:
            raise ValueError("One of condition must be set")

    def get_q(self):
        """Return instance queryset"""
        q = m_q()
        if self.labels:
            q &= m_q(effective_labels_all=self.labels)
        if self.groups:
            q &= m_q(effective_service_groups__all=self.groups)
        return q

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.groups:
            r["service_groups"] = {"$all": list(self.groups)}
        if self.wf_states:
            r["state"] = {"$in": [str(x.id) for x in self.wf_states]}
        if self.remote_system:
            r["remote_system"] = str(self.remote_system.name)
        return r


@tree(field="replace_rule")
@on_delete_check(check=[("sa.ReactionRule", "replace_rule")])
@change
@bi_sync
class ReactionRule(Document):
    meta = {
        "collection": "reactionrules",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "sa.eventreactionrules",
        "json_depends_on": ["inv.capabilities", "fm.alarmclasses"],
        "json_unique_fields": ["name"],
        "indexes": [("is_active", "object_model", "conditions")],
    }

    name = StringField(unique=True)
    description = StringField()
    uuid = UUIDField(binary=True)
    is_active = BooleanField(default=True)
    preference = IntField(required=True, default=1000)
    # Replace Rule
    replace_rule_policy = StringField(
        required=True,
        choices=[
            ("D", "Disable"),
            ("w", "Whole"),
            ("c", "Extend Condition"),
            ("a", "Action"),
        ],
        default="a",
    )
    replace_rule: Optional["ReactionRule"] = ReferenceField("self", required=False)
    # Conditions
    # Register from Model
    object_model = StringField(
        choices=list(REACTION_MODELS),
        required=True,
    )
    conditions: List["Match"] = EmbeddedDocumentListField(Match)
    execute_policy = StringField(
        choices=[
            ("J", "As Job"),
            ("A", "Job with Approve"),
            ("R", "Immediate"),
        ],
        default="R",
    )
    stop_processing = BooleanField(default=False)
    # Match Handler -> ChangedItem ->
    operations: List[str] = ListField(
        StringField(
            choices=[
                "create",
                "update",
                "delete",
                "topology",
                "config_changed",
                "version_changed",
                "version_set",
                "any",
            ],
            default="any",
        ),
    )
    # Context
    field_data: List["FieldData"] = EmbeddedDocumentListField(FieldData)
    affected_domains: List["ConfigurationDomain"] = EmbeddedDocumentListField(ConfigurationDomain)
    # Controller, Scenario
    # Action Commands Set
    action_command_set: List["ActionCommands"] = EmbeddedDocumentListField(ActionCommands)
    # Actions
    action_common: List[ActionItem] = EmbeddedDocumentListField(ActionItem)
    # Notification
    notification_policy = StringField(
        choices=[("D", "disable"), ("R", "register"), ("G", "To Group")],
        default="D",
    )
    notification_group: Optional["NotificationGroup"] = ForeignKeyField(
        NotificationGroup, required=False
    )
    subject_template = StringField()
    # Validation
    action_script: Optional[str] = StringField(required=False)
    # Diagnostic, State Needed
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _rule_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ReactionRule"]:
        return ReactionRule.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["ReactionRule"]:
        return ReactionRule.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["ReactionRule"]:
        return ReactionRule.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rule_cache"), lock=lambda _: id_lock)
    def get_rules_matcher(cls, model_id: str, operation: str) -> Tuple[Tuple[str, Callable], ...]:
        """Build matcher based on Profile Match Rules"""
        r = {}
        for rule in ReactionRule.objects.filter(
            is_active=True,
            object_model=model_id,
            operations__in=[operation],
        ):
            r[(str(rule.id), rule.preference)] = rule.get_matcher()
        return tuple((x[0], r[x]) for x in sorted(r, key=lambda i: i[1]))

    # def get_json_path(self) -> Path:
    #     return Path(*(quote_safe_path(n.strip()) for n in self.name.split("|"))).with_suffix(
    #         ".json"
    #     )

    def get_matcher(self) -> Optional[Callable]:
        """Build matcher structure"""
        expr = []
        for mr in self.conditions or []:
            expr.append(mr.get_match_expr())
        # AND
        for mf in self.field_data or []:
            e = mf.get_match_expr()
            if e:
                expr.append(e)
        if not expr:
            return None
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def is_match(self, o) -> bool:
        """Local Match rules"""
        matcher = self.get_matcher()
        if not matcher:
            return True
        ctx = o.get_matcher_ctx()
        return matcher(ctx)

    def get_effective_rule(self) -> Optional["ReactionRule"]:
        """Effective rule for Replace Rule settings"""
        return self

    @classmethod
    def iter_rules(cls, model_id: str, operation: str, m_ctx: Dict[str, Any]) -> Iterable[str]:
        """Iterate rule for object"""
        for rule_id, match in cls.get_rules_matcher(model_id, operation):
            if not match or match(m_ctx):
                yield rule_id
                # check Stop processing
        return None

    def get_action_ctx(self, o) -> Dict[str, Any]:
        """Create action context (to env)"""
        r = {"obj": o}
        # managed_object
        if isinstance(o, ManagedObject):
            r["managed_object"] = o
        elif hasattr(o, "managed_object"):
            r["managed_object"] = o.managed_object
        caps = o.get_caps()
        for i in self.field_data:
            if i.field and hasattr(o, i.field):
                name = i.set_context or i.field
                r[name] = getattr(o, i.field, None)
            if caps and i.capability and i.capability.name in caps:
                name = i.set_context or i.capability.name
                r[name] = caps[i.capability.name]
        return r

    def get_action_commands_job(
        self, managed_object, **kwargs
    ) -> Tuple[ManagedObject, List[JobRequest]]:
        """Return as Job Request"""
        r = []
        for a in self.action_command_set:
            req = a.action.get_job_request(managed_object=managed_object, **kwargs)
            if self.execute_policy == "A":
                req.require_approval = True
            r.append(req)
        return managed_object, r

    def get_action_commands(
        self, managed_object: ManagedObject, **ctx
    ) -> Tuple[ManagedObject, List[str], bool]:
        """Return As Config"""
        r, cfg_mode = [], False
        for a in self.action_command_set:
            commands, cfg = a.action.get_execute_commands(managed_object, dry_run=True, **ctx)
            cfg_mode |= cfg.config_mode
            # Exit from mode/Raise error when mode changed
            r.append(commands)
        return managed_object, r, cfg_mode

    def iter_actions(self, o) -> List[Tuple[ActionType, Dict[str, Any], JobRequest]]:
        """
        1. Handler
        2. Script/Command Action
        3. Object Action
        4. Notify
        """
        for a in self.action_common:
            if not a.action.is_supported(o):
                continue
            cfg = a.get_config()
            if cfg:
                yield a.action, cfg, a.action.get_job(o, **cfg)

    def get_config(self):
        """Getting config for router"""

    @classmethod
    def register_change(cls, item: ChangeItem):
        """Register change and apply rules"""
        o = item.instance
        if not o:
            return
        if hasattr(o, "get_matcher_ctx"):
            ctx = o.get_matcher_ctx()
        else:
            ctx = {}
        # Getting rule
        for rule_id in ReactionRule.iter_rules(item.model_id, item.op, ctx):
            rule = ReactionRule.get_by_id(rule_id)
            # run actions
            rule.run(o)
        # Lookup Domain ?

    def run(self, o, dry_run: bool = True):
        """Execute actions"""
        # Mege Action by Managed Object -. Actions
        # Run: As Command, As Job
        for action, cfg, _ in self.iter_actions(o):
            r = action.run_action(o, **cfg)
            # Processed result
            # Delayed processed
            self.processed_result(o, r)
        # Action Command
        ctx = self.get_action_ctx(o)  # get_env, Processed Data
        if self.execute_policy == "R":
            mo, commands, cfg_required = self.get_action_commands(**ctx)
            mo.scripts.commands(
                commands=[commands],
                config_mode=cfg_required,
                dry_run=dry_run,
            )
        else:
            mo, jobs = self.get_action_commands_job(**ctx)
            req = JobRequest(name=f"Reaction On {o} bu Rule {self.name}", jobs=jobs)
            # Locks for ManagedObject
            req.submit()
        # Configuration Domain
        # Configuration Domain Ctx
        # iter_topology
        # get_effective_path ? multiple path
        # Send Result
        # if self.notification_policy == "G" and self.notification_group:
        #    self.notification_group.render_message()

    def processed_result(self, o, result):
        """Result operation"""
        # Success
        # Failed
        # Register Result to Audit
