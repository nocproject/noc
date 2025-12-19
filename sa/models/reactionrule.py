# ---------------------------------------------------------------------
# Object Event Reaction Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import operator
import logging
from threading import Lock
from typing import Optional, List, Union, Dict, Any, Callable, Tuple, Iterable

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
from noc.wf.models.state import State
from noc.models import get_model
from noc.core.models.cfgactions import ActionType
from noc.core.matcher import build_matcher
from noc.core.runner.job import JobRequest
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.change.model import ChangeItem
from noc.core.change.policy import REACTION_MODELS
from noc.core.model.decorator import tree, on_delete_check
from noc.core.text import quote_safe_path

id_lock = Lock()
rule_lock = Lock()
matcher_lock = Lock()

react_logger = logging.getLogger(__name__)


class ActionItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    action: ActionType = EnumField(ActionType, required=True)
    commands: Action = PlainReferenceField(Action)
    run: str = StringField(
        choices=[
            ("A", "Always"),
            ("F", "Prev Failed"),
            ("S", "Prev Success"),
            # ("L", "All Success")
            # ("P", "Partially") Move to Affected ?
        ],
        default="A",
    )
    handler: "Handler" = PlainReferenceField(Handler, required=False)
    # End Commands Run
    allow_fail: bool = BooleanField(default=True)
    is_fatal: bool = BooleanField(default=False)
    # repeat: bool = BooleanField(default=True)
    # RollBack policy
    # End, Wait, Rollback
    cancel_command = BooleanField(default=False)
    # Ctx
    context = ListField(StringField())
    # transmute Ctx
    expand_domain_ctx = BooleanField(default=False)
    # Apply over Topology
    over_topology = BooleanField(default=False)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "action": self.action.value,
            "run": self.run,
            "allow_fail": self.allow_fail,
            "cancel_command": self.cancel_command,
        }
        if self.context:
            r["context"] = list(self.context)
        if self.commands:
            r["commands__name"] = self.commands.name
        # if self.interaction_audit:
        #    r["interaction_audit"] = self.interaction_audit.value
        if self.handler:
            r["handler__name"] = list(self.handler.name)
        return r

    def get_context(self) -> Dict[str, str]:
        """"""
        r = {}
        for c in self.context:
            key, *value = c.split(":")
            if value:
                r[key] = value[0]
        return r

    def get_config(self, **kwargs) -> Dict[str, Any]:
        """Get Action config from Ctx"""
        key, args = None, {}
        match self.action:
            case ActionType.ACTION_COMMAND:
                key = self.commands.name
            case ActionType.FIRE_WF_EVENT:
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


class AffectedRule(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    model_id: str = StringField(required=False)
    op: str = StringField(default="topology")
    rule: Optional["ReactionRule"] = PlainReferenceField("sa.ReactionRule", required=False)
    # RollBack Rule
    # Affected DataStream
    # datastream = StringField(required=False)
    # Add Result to Ctx
    extend_ctx: bool = BooleanField(default=False)
    suppress_action: bool = BooleanField(default=False)
    # Handler for manupulate ctx/Transmute ctx
    #


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
                "config",
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
    affected_rules: List["AffectedRule"] = EmbeddedDocumentListField(AffectedRule)
    # Controller, Scenario
    # Action Commands Set
    # action_command_set: List["ActionCommands"] = EmbeddedDocumentListField(ActionCommands)
    # Actions
    actions: List[ActionItem] = EmbeddedDocumentListField(ActionItem)
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
    _matcher_cache = cachetools.TTLCache(100, ttl=120)

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
    @cachetools.cachedmethod(operator.attrgetter("_rule_cache"), lock=lambda _: rule_lock)
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

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    def iter_rules(cls, model_id: str, operation: str, m_ctx: Dict[str, Any]) -> Iterable["str"]:
        """Iterate rule for object"""
        for rule_id, match in cls.get_rules_matcher(model_id, operation):
            if not match or match(m_ctx):
                yield rule_id
                # check Stop processing

    @classmethod
    def register_change(cls, item: ChangeItem, dry_run: bool = False):
        """Register Item change"""
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
            rule.run(o, domains=item.domains, dry_run=dry_run)

    @classmethod
    def register_event(cls, event: Any, dry_run: bool = False):
        """Register Event for reaction"""

    @cachetools.cachedmethod(
        operator.attrgetter("_matcher_cache"),
        lock=lambda _: matcher_lock,
        key=operator.attrgetter("id"),
    )
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

    def get_action_ctx(self, o) -> Dict[str, Any]:
        """Create action context (to env)"""
        # r = {"obj": o}
        r = {}
        if hasattr(o, "get_action_ctx"):
            r |= o.get_action_ctx()
        if hasattr(o, "get_caps"):
            caps = o.get_caps()
        else:
            caps = {}
        for i in self.field_data:
            if i.field and hasattr(o, i.field):
                name = i.set_context or i.field
                r[name] = getattr(o, i.field, None)
            if caps and i.capability and i.capability.name in caps:
                name = i.set_context or i.capability.name
                r[name] = caps[i.capability.name]
        return r

    def iter_actions(self, o) -> List[Tuple[ActionType, Dict[str, Any], JobRequest]]:
        """
        1. Handler
        2. Script/Command Action
        3. Object Action
        4. Notify
        """
        for a in self.actions:
            if not a.action.is_supported(o):
                continue
            cfg = a.get_config()
            if cfg:
                yield a.action, cfg, a.action.get_job(o, **cfg)

    def get_config(self):
        """Getting config for router"""

    def iter_affected_rules(
        self,
        domains: List[Any],
    ) -> Iterable[Tuple["ReactionRule", Any, "AffectedRule"]]:
        """Iterate over affected Rules"""
        # self ?
        for model_id, oid in domains or []:
            m = get_model(model_id)
            o = m.get_by_id(oid)
            m_ctx = o.get_matcher_ctx()
            # yield ctx
            for a_rule in self.affected_rules:
                if a_rule.model_id and a_rule.model_id != model_id:
                    continue
                if a_rule.rule:
                    yield a_rule.rule, o, a_rule
                    continue
                for rule_id in ReactionRule.iter_rules(model_id, a_rule.op, m_ctx):
                    rule = ReactionRule.get_by_id(rule_id)
                    yield rule, o, a_rule

    def run_actions(
        self,
        o: Any,
        user: Optional[Any] = None,
        dry_run: bool = False,
        logger: Optional[logging.Logger] = None,
        **kwargs,
    ):
        """"""
        logger = logger or react_logger
        jobs = []
        ctx = self.get_action_ctx(o)
        ctx |= kwargs
        logger.info("[%s] Run Action for rule: '%s' in context: %s", self.name, o, ctx)
        for num, ra in enumerate(self.actions):
            if ra.run != "A":
                continue
            if not ra.action.is_supported(o):
                logger.info("[%s] Not supported Action '%s' for: %s", self.name, ra.action, str(o))
                continue
            ctx = ra.get_context()
            ctx |= kwargs
            cfg = ra.get_config(**ctx)
            if self.execute_policy == "R":
                r = ra.action.run_action(
                    o, key=cfg.pop("key"), cfg=cfg, user=user, dry_run=dry_run, **ctx
                )
                self.processed_result(o, r)
            else:
                req = ra.action.get_job_request(o, cfg=cfg, user=user, dry_run=dry_run, **ctx)
                if self.execute_policy == "A":
                    req.require_approval = True
                jobs.append(req)
        if jobs:
            req = JobRequest(name=f"Reaction On {o} bu Rule {self.name}", jobs=jobs)
            # Locks for ManagedObject
            req.submit()

    def run(
        self,
        o: Any,
        domains: Optional[List[Tuple[str, str]]] = None,
        user: Optional[Any] = None,
        dry_run: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        """Run Rule for instance"""
        # logger = logger or react_logger
        processed_rule = set()
        domain_ctx = {}
        acton_ctx = self.get_action_ctx(o)
        # Reaction - Action API (Topology ?)
        # Locks for ManagedObject
        for rule, domain, cfg in self.iter_affected_rules(domains):
            if rule.id in processed_rule:
                continue
            if cfg.extend_ctx:
                domain_ctx |= rule.get_action_ctx(domain)
                domain_ctx["domain"] = domain
            processed_rule.add(rule.id)
            if cfg.suppress_action:
                continue
            rule.run_actions(domain, user=user, dry_run=dry_run, logger=logger, **acton_ctx)
        # Add Domain Ctx
        # Action Command, Required ManagedObject ? Process Topology
        # Result API
        self.run_actions(o, user=user, dry_run=dry_run, logger=logger, **domain_ctx)
        # Mege Action by Managed Object -. Actions
        # Run: As Command, As Job
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
