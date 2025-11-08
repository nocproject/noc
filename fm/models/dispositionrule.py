# ---------------------------------------------------------------------
# Disposition Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path
import operator
import re
from threading import Lock
from typing import Optional, List, Union, Dict, Any, Callable

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    LongField,
    IntField,
    UUIDField,
    ReferenceField,
    EmbeddedDocumentListField,
    EnumField,
    ObjectIdField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.main.models.label import Label
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.action import Action
from noc.fm.models.eventclass import EventClass
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.enumeration import Enumeration
from noc.sa.models.interactionlog import Interaction
from noc.core.models.cfgactions import ActionType
from noc.core.models.valuetype import ValueType
from noc.core.fm.enum import EventAction
from noc.core.matcher import build_matcher
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.model.decorator import tree, on_delete_check
from noc.core.prettyjson import to_json
from noc.core.path import safe_json_path

id_lock = Lock()


class VarItem(EmbeddedDocument):
    """
    Variable Manipulation Structure.
    Map variable to slot, resolve object and resources by set
    Attributes:
        name: Variable name
        wildcard: wildcard label for set value
        required: Required Fields
        condition: Match condition
        value: Match value by condition

    """

    meta = {"strict": False, "auto_create_index": False}

    # key
    name = StringField(required=True)
    wildcard = ReferenceField(Label, required=False)
    required = BooleanField(default=True)
    # Condition
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
        ],
        default="eq",
    )
    value = StringField(required=False)
    choices = ListField(StringField(), required=False)
    # Normalize
    enum = PlainReferenceField(Enumeration)
    value_type: ValueType = EnumField(ValueType, required=False)
    alias = StringField(required=False)
    # Affected
    affected_model = StringField(required=False)
    update_oper_status: str = StringField(
        choices=[("N", "Disable"), ("U", "UP"), ("D", "Down"), ("V", "By Var")],
        default="N",
    )

    def __str__(self):
        if self.condition:
            return f"{self.name}: {self.condition} {self.value}"
        return f"{self.name}: AL({self.alias}), A({self.affected_model})"

    def get_match_expr(self) -> Dict[str, Any]:
        """"""
        if self.condition == "exists" and self.value:
            return {"vars": {"$in": [self.value]}}
        if self.condition == "in" and self.choices:
            return {self.name: {"$any": self.choices}}
        if not self.value:
            return {}
        return {self.name: {f"${self.condition}": self.value}}

    def get_config(self):
        """Getting Mapping Config"""
        r = {"name": self.name, "required": self.required}
        if self.value_type:
            r["value_type"] = self.value_type.value
        if self.affected_model:
            r |= {
                "affected_model": self.affected_model,
                "update_oper_status": self.update_oper_status,
            }
        if self.alias:
            r["alias"] = self.alias
        return r

    def get_action_config(self) -> Optional[Dict[str, Any]]:
        if self.update_oper_status in {"N", "V"}:
            return None
        return {
            "action": ActionType.SET_OPER_STATE,
            "key": "",
            "args": {"status": self.update_oper_status == "U"},
            "model_id": self.affected_model,
        }

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"name": self.name, "required": self.required}
        if self.wildcard:
            r["wildcard__name"] = self.wildcard.name
        if self.condition:
            r |= {"condition": self.condition, "value": self.value}
        if self.enum:
            r["enum__name"] = self.enum.name
        if self.alias:
            r["alias"] = self.alias
        if self.affected_model:
            r |= {
                "affected_model": self.affected_model,
                "update_oper_status": self.update_oper_status,
            }
        return r


class Match(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    # categories: List[EventCategory] = ListField(ReferenceField(EventCategory, required=True))
    # ex_categories: List[EventCategory] = ListField(ReferenceField(EventCategory, required=True))
    event_class_re: str = StringField()
    groups: List[ResourceGroup] = ListField(ReferenceField(ResourceGroup, required=True))
    ex_groups: List[ResourceGroup] = ListField(ReferenceField(ResourceGroup, required=True))
    # severity: AlarmSeverity = ReferenceField(AlarmSeverity, required=False)
    remote_system: Optional["RemoteSystem"] = ReferenceField(RemoteSystem, required=False)
    reference_rx = StringField()
    event_classes: List[ObjectId] = ListField(ObjectIdField(required=True))
    object_status: Optional[str] = StringField(
        choices=[("A", "Any"), ("U", "To Up"), ("D", "To Down")],
        required=False,
    )

    def __str__(self):
        return f"{', '.join(self.labels)}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {}
        if self.event_class_re:
            r["event_class_re"] = self.event_class_re
        if self.object_status in ("D", "U"):
            r["object_status"] = self.object_status
        if self.reference_rx:
            r["reference_rx"] = self.reference_rx
        return r

    def clean(self):
        ec = (self.event_class_re or "").strip()
        if not ec:
            self.event_classes = []
        elif EventClass.get_by_name(ec):
            ec = EventClass.get_by_name(ec)
            self.event_classes = [ec.id]
        else:
            self.event_classes = [ec.id for ec in EventClass.objects.filter(name=re.compile(ec))]
        super().clean()

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.groups:
            r["service_groups"] = {"$all": [str(x.id) for x in self.groups]}
        if self.remote_system:
            r["remote_system"] = str(self.remote_system.id)
        if self.object_status in ("D", "U"):
            r["object_avail"] = {"$eq": {"U": True, "D": False}[self.object_status]}
        if self.reference_rx:
            r["reference"] = {"$regex": self.reference_rx}
        # if self.name_patter:
        #     r["name"] = {"$regex": self.name_patter}
        # if self.description_patter:
        #     r["description"] = {"$regex": self.description_patter}
        return r


class AlarmRootCauseCondition(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    alarm_class: AlarmClass = PlainReferenceField(AlarmClass, required=True)
    window = IntField(required=True)
    # Match Object (resource) ?
    topology_rca = BooleanField(default=False)
    affected_service = BooleanField(default=False)
    # affected_resource = BooleanField(default=False)


class ActionItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    # Action API ? by object, move to instance ?
    action: ActionType = EnumField(ActionType, required=True)
    action_command: Optional["Action"] = ReferenceField(Action, required=False)
    interaction_audit: Optional[Interaction] = EnumField(Interaction, required=False)
    context: List[str] = ListField(StringField())

    def __str__(self):
        return f"C: {self.action}; A: {self.interaction_audit}; С: {self.action_command}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"action": self.action.value}
        if self.action_command:
            r["action_command__name"] = self.action_command.name
        if self.interaction_audit:
            r["interaction_audit"] = self.interaction_audit.value
        if self.context:
            r["contex"] = list(self.context)
        return r

    def get_config(self) -> Dict[str, Any]:
        """Get Action config"""
        key, args = None, {}
        match self.action:
            case ActionType.ACTION_COMMAND:
                key = self.action_command.name
            case ActionType.AUDIT_COMMAND:
                key = str(self.interaction_audit.value)
                # "args": {"audit": self.interaction_audit.value},
            # case ActionType.FIRE_WF_EVENT:
            #    key = self.
            case ActionType.RUN_DISCOVERY:
                key = ""
                if self.interaction_audit:
                    args = {"audit": self.interaction_audit}
        if key is not None:
            return {"action": self.action.value, "key": key, "args": args}
        return {}


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
@on_delete_check(check=[("fm.DispositionRule", "replace_rule")])
@change
@bi_sync
class DispositionRule(Document):
    meta = {
        "collection": "dispositionrules",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.dispositionrules",
        "json_depends_on": ["fm.alarmseverities", "fm.alarmclasses"],
        "json_unique_fields": ["name"],
    }

    name = StringField(unique=True)
    description = StringField()
    uuid = UUIDField(binary=True)
    is_active = BooleanField(default=True)
    preference = IntField(required=True, default=1000)
    conditions: List[Match] = EmbeddedDocumentListField(Match)
    # vars_conditions: List[MatchData] = EmbeddedDocumentListField(MatchData)
    vars_op: List[VarItem] = EmbeddedDocumentListField(VarItem)
    vars_conditions_op: str = StringField(
        choices=[
            ("AND", "Raise Disposition Alarm"),
            ("OR", "Clear Disposition Alarm"),
        ],
        default="AND",
    )
    # time_pattern
    # Combo Condition
    combo_condition = StringField(
        required=False,
        default="none",
        choices=[
            (x, x)
            for x in (
                # Apply action immediately
                "none",
                # Apply when event firing rate
                # exceeds combo_count times during combo_window
                "frequency",
                # Apply action if event followed by all combo events
                # in strict order
                "sequence",
                # Apply action if event followed by all combo events
                # in no specific order
                "all",
                # Apply action if event followed by any of combo events
                "any",
                # Only Change !!!!
            )
        ],
    )
    # Time window for combo events in seconds
    combo_window = IntField(required=False, default=0)
    # Applicable for frequency.
    combo_count = IntField(required=False, default=0)
    # Applicable for sequence, all and any combo_condition
    combo_event_classes = ListField(
        PlainReferenceField("fm.EventClass"), required=False, default=[]
    )
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
    replace_rule: Optional["DispositionRule"] = ReferenceField("self", required=False)
    # Actions
    handlers: List[HandlerItem] = EmbeddedDocumentListField(HandlerItem)
    notification_group: Optional["NotificationGroup"] = ForeignKeyField(
        NotificationGroup, required=False
    )
    subject_template = StringField()
    target_actions: List[ActionItem] = EmbeddedDocumentListField(ActionItem)
    default_action = StringField(
        choices=[
            ("R", "Raise Disposition Alarm"),
            ("C", "Clear Disposition Alarm"),
            ("I", "Ignore Disposition Alarm"),
            ("D", "Drop Event"),
            ("F", "Drop Event (with MX)"),
        ],
        required=False,
    )
    # allow_update
    alarm_disposition: Optional["AlarmClass"] = PlainReferenceField(AlarmClass, required=False)
    # RCA
    # root_cause = EmbeddedDocumentListField(AlarmRootCauseCondition)
    #
    # severity_policy = StringField(
    #     choices=[
    #         ("CB", "Class Based Policy"),
    #         ("AB", "Affected Based Severity Preferred"),
    #         ("AL", "Affected Limit"),
    #         ("ST", "By Tokens"),
    #     ],
    #     default="AL",
    # )
    stop_processing = BooleanField(default=False)
    # TTL ?
    # BI ID
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_AC_NAME = "Group"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["DispositionRule"]:
        return DispositionRule.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["DispositionRule"]:
        return DispositionRule.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["DispositionRule"]:
        return DispositionRule.objects.filter(bi_id=bi_id).first()

    def iter_changed_datastream(self, changed_fields=None):
        for ec in self.get_event_classes():
            yield "cfgevent", f"ec:{ec.id}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "preference": self.preference,
            "stop_processing": self.stop_processing,
        }
        if self.conditions:
            r["conditions"] = [m.json_data for m in self.conditions]
        if self.vars_op:
            r["vars"] = [m.json_data for m in self.vars_op]
            r["vars_conditions_op"] = self.vars_conditions_op
        if self.replace_rule:
            r |= {
                "replace_rule__name": self.replace_rule.name,
                "replace_rule_policy": self.replace_rule_policy,
            }
        if self.target_actions:
            r["target_actions"] = [m.json_data for m in self.target_actions]
        if self.combo_condition and self.combo_event_classes:
            r |= {
                "combo_condition": self.combo_condition,
                "combo_window": self.combo_window,
                "combo_count": self.combo_count,
                "combo_event_classes__name": [ec.name for ec in self.combo_event_classes],
            }
        if self.alarm_disposition:
            r |= {
                "alarm_disposition__name": self.alarm_disposition.name,
                "default_action": self.default_action,
            }
        if self.handlers:
            r["handlers"] = [h.json_data for h in self.handlers]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "preference",
                "disposition__name",
                "combo_condition",
                "combo_window",
                "combo_count",
            ],
        )

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)

    def get_event_classes(self):
        r = []
        for rr in self.conditions:
            if not rr.event_class_re:
                continue
            ec = EventClass.objects.get(name=rr.event_class_re)
            if ec:
                r.append(ec)
            else:
                r += list(EventClass.objects.filter(name=re.compile(rr.event_class_re)))
        return r

    def get_matcher(self) -> Optional[Callable]:
        """Getting matcher for rule"""
        expr = []
        if not self.conditions:
            return None
        for r in self.conditions:
            expr.append(r.get_match_expr())
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    @classmethod
    def get_event_actions(cls, event_class: EventClass):
        """Build Event action Rules"""
        r = []
        for rule in DispositionRule.objects.filter(
            conditions__event_class_re=event_class.name,
            is_active=True,
        ).order_by("preference"):
            r.append(DispositionRule.get_event_rule_config(rule))
        return r

    @classmethod
    def get_event_rule_config(cls, rule: "DispositionRule") -> Dict[str, Any]:
        """Disposition Rule config"""
        if rule.replace_rule and rule.replace_rule_policy == "w":
            # Merge Rule ?
            return DispositionRule.get_event_rule_config(rule.replace_rule)
        r = {
            "name": rule.name,
            "is_active": rule.is_active,
            "preference": rule.preference,
            "alarm_class": None,
            "stop_processing": rule.stop_processing,
            # disposition_var_map
            "match_expr": {},
            "vars_match_expr": {},
            "action": EventAction.LOG.value,
            "target": {"model": "sa.ManagedObject"},
            "actions": [],
        }
        if rule.default_action:
            r["action"] = EventAction.from_rule(rule.default_action).value
        if rule.alarm_disposition and rule.default_action in "RC":
            r["alarm_class"] = rule.alarm_disposition.name
        for ta in rule.target_actions:
            ta = ta.get_config()
            if ta:
                r["actions"].append(ta)
        or_condition = []
        for c in rule.vars_op:
            cfg = c.get_action_config()
            if cfg:
                r["actions"].append(cfg)
            m = c.get_match_expr()
            if not m:
                continue
            if rule.vars_conditions_op == "OR":
                or_condition.append(m)
            else:
                r["vars_match_expr"] |= m
        if or_condition:
            r["vars_match_expr"]["$or"] = or_condition
        if rule.notification_group:
            r |= {
                "notification_group": str(rule.notification_group.id),
                "subject_template": rule.subject_template,
            }
        if rule.handlers:
            r["handlers"] = [str(h.handler.handler) for h in rule.handlers]
        if not rule.conditions:
            return r
        rule_conditions = []
        for c in rule.conditions:
            if c.object_status in ("D", "U"):
                r["object_avail_condition"] = {"U": True, "D": False}[c.object_status]
                continue
            expr = c.get_match_expr()
            if not expr:
                continue
            rule_conditions.append(expr)
        if len(rule_conditions) == 1:
            r["match_expr"] = rule_conditions[0]
        elif rule_conditions:
            r["match_expr"] = {"$or": rule_conditions}
        return r

    @classmethod
    def get_event_alarm_rule_config(cls, rule: "DispositionRule") -> Dict[str, Any]:
        """Build Rule for Disposition processing"""
        if rule.replace_rule and rule.replace_rule_policy == "w":
            # Merge Rule ?
            return DispositionRule.get_event_rule_config(rule.replace_rule)
        r = {
            "name": rule.name,
            "is_active": rule.is_active,
            "preference": rule.preference,
            "stop_processing": rule.stop_processing,
            # disposition_var_map
            "match_expr": {},
            "vars_match_expr": {},
            "vars_transform": [],
            "event_classes": [],
            "action": "ignore",
        }
        if rule.default_action:
            r["action"] = {"R": "raise", "C": "clear", "I": "ignore", "D": "drop", "F": "drop_mx"}[
                rule.default_action
            ]
        or_condition, vars_transform = [], []
        for c in rule.vars_op:
            cfg = c.get_config()
            if cfg:
                vars_transform.append(cfg)
            m = c.get_match_expr()
            if not m:
                continue
            if rule.vars_conditions_op == "OR":
                or_condition.append(m)
            else:
                r["vars_match_expr"] |= m
        if or_condition:
            r["vars_match_expr"]["$or"] = or_condition
        if vars_transform:
            r["vars_transform"] = vars_transform
        if not rule.conditions:
            return r
        rule_conditions = []
        for c in rule.conditions:
            if c.object_status in ("D", "U"):
                r["object_avail_condition"] = {"U": True, "D": False}[c.object_status]
                continue
            expr = c.get_match_expr()
            if not expr:
                continue
            rule_conditions.append(expr)
        if len(rule_conditions) == 1:
            r["match_expr"] = rule_conditions[0]
        elif rule_conditions:
            r["match_expr"] = {"$or": rule_conditions}
        r["event_classes"] = [str(x.id) for x in rule.get_event_classes()]
        if not r["event_classes"]:
            r["reference_lookup"] = True
        return r
