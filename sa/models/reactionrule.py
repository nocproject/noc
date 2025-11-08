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
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.capability import Capability
from noc.sa.models.action import Action
from noc.fm.models.alarmclass import AlarmClass
from noc.wf.models.state import State
from noc.core.models.cfgactions import ActionType
from noc.core.matcher import build_matcher
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.change.model import ChangeItem
from noc.core.change.policy import REACTION_MODELS
from noc.core.model.decorator import tree, on_delete_check

id_lock = Lock()


class FieldData(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    field = StringField(required=False)
    capability: Optional[Capability] = ReferenceField(Capability)
    # operations: List[str] = ListField(StringField(
    #     choices=["create", "update", "delete", "topology", "any"], default="any"),
    # )
    op = StringField(
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
        return f"{self.field} {self.op} {self.value}"

    def clean(self):
        super().clean()
        if not self.field and not self.capability:
            raise ValueError("Field or Caps Must Be set")

    def get_match_expr(self) -> Dict[str, Any]:
        """"""
        if self.capability:
            return {"caps": {"$in": [self.capability.name]}}
        # Field matcher
        return {self.field: {f"${self.op}": self.value}}

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"field": self.field, "op": self.op, "value": self.value}


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


class HandlerItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    # On Event, On Raise, On Close
    handler: "Handler" = ReferenceField(Handler, required=True)

    @property
    def json_data(self) -> Dict[str, Any]:
        if self.handler:
            return {"handler__name": self.handler.name}
        return {}


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
    field_data: List["FieldData"] = EmbeddedDocumentListField(FieldData)
    # Action
    # Handlers
    handlers: List["HandlerItem"] = EmbeddedDocumentListField(HandlerItem)
    # Notification
    notification_policy = StringField(
        choices=[("D", "disable"), ("R", "register"), ("G", "To Group")],
        default="D",
    )
    notification_group: Optional["NotificationGroup"] = ForeignKeyField(
        NotificationGroup, required=False
    )
    subject_template = StringField()
    # alarm
    alarm_disposition: Optional["AlarmClass"] = PlainReferenceField(AlarmClass, required=False)
    # Run Discovery
    # Validation
    action_command: Optional["Action"] = ReferenceField(Action, required=False)
    action_script: Optional[str] = StringField(required=False)
    # Controller, Scenario
    # fire_event
    # failed_event
    # success_event
    # ttl
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
            expr.append(mf.get_match_expr())
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
        caps = o.get_caps()
        for i in self.field_data:
            if i.field and hasattr(o, i.field):
                name = i.set_context or i.field
                r[name] = getattr(o, i.field, None)
            if caps and i.capability and i.capability.name in caps:
                name = i.set_context or i.capability.name
                r[name] = caps[i.capability.name]
        return r

    def get_actions(self, o) -> List[Tuple[ActionType, str]]:
        """
        1. Handler
        2. Script/Command Action
        3. Object Action
        4. Notify
        """
        ctx = self.get_action_ctx(o)  # get_env, Processed Data
        for h in self.handlers:
            yield ActionType.HANDLER, str(h.handler.handler), {}
        if self.action_command:
            yield ActionType.ACTION_COMMAND, str(self.action_command.name), ctx

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

    def run(self, o):
        """Execute actions"""
        for action, key, cfg in self.get_actions(o):
            r = action.run_action(o, key, cfg)
            # Processed result
            # Delayed processed
            self.processed_result(o, r)
        # Send Result
        # if self.notification_policy == "G" and self.notification_group:
        #    self.notification_group.render_message()

    def processed_result(self, o, result):
        """Result operation"""
        # Success
        # Failed
        # Register Result to Audit
