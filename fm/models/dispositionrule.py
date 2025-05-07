# ---------------------------------------------------------------------
# Disposition Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
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
    EmbeddedDocumentField,
    EnumField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.action import Action
from noc.fm.models.eventclass import EventClass
from noc.sa.models.interactionlog import Interaction
from noc.core.matcher import build_matcher
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.model.decorator import tree, on_delete_check
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.fm.models.alarmclass import AlarmClass


id_lock = Lock()


class MatchData(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    field = StringField(required=True)
    op = StringField(
        choices=[
            "regex",
            "contains",
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
    choices = ListField(StringField(required=True))

    def __str__(self):
        return f"{self.field} {self.op} {self.value}"

    def get_match_expr(self) -> Dict[str, Any]:
        """"""
        if self.field == "vars":
            return {self.field: {"$in": self.value}}
        if self.choices:
            # ?OR
            return {self.field: {"$any": self.choices}}
        return {self.field: {f"${self.op}": self.value}}

    @property
    def json_data(self) -> Dict[str, Any]:
        if self.choices:
            return {"field": self.field, "op": self.op, "choices": self.choices}
        return {"field": self.field, "op": self.op, "value": self.value}


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    # categories: List[EventCategory] = ListField(ReferenceField(EventCategory, required=True))
    # ex_categories: List[EventCategory] = ListField(ReferenceField(EventCategory, required=True))
    event_class_re: str = StringField()
    groups: List[ResourceGroup] = ListField(ReferenceField(ResourceGroup, required=True))
    ex_groups: List[ResourceGroup] = ListField(ReferenceField(ResourceGroup, required=True))
    # severity: AlarmSeverity = ReferenceField(AlarmSeverity, required=False)
    remote_system: Optional["RemoteSystem"] = ReferenceField(RemoteSystem, required=False)

    def __str__(self):
        return f'{", ".join(self.labels)}'

    @property
    def json_data(self) -> Dict[str, Any]:
        if self.event_class_re:
            return {"event_class_re": self.event_class_re}
        return {}

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.groups:
            r["service_groups"] = {"$all": [str(x.id) for x in self.groups]}
        if self.remote_system:
            r["remote_system"] = str(self.remote_system.name)
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


class ObjectActionItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    # Action API ? by object, move to instance ?
    action_command: Optional["Action"] = ReferenceField(Action, required=False)
    interaction_audit: Optional[Interaction] = EnumField(Interaction, required=False)
    run_discovery: bool = BooleanField(default=False)
    update_avail_status = StringField(
        choices=[("N", "Disable"), ("A", "Available"), ("U", "Unavail")],
        default="N",
    )
    # resource as context
    # Set Diagnostic
    # affected_service ?
    # Update Resource State (workflow)
    # TTL


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
    #
    conditions: List[Match] = EmbeddedDocumentListField(Match)
    #
    vars_conditions: List[MatchData] = EmbeddedDocumentListField(MatchData)
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
    #
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
    object_actions: Optional["ObjectActionItem"] = EmbeddedDocumentField(
        ObjectActionItem, required=False
    )
    update_oper_status = StringField(
        choices=[
            ("N", "Disable"),
            ("D", "Set Down"),
            ("U", "Set Up"),
            ("V", "By Var (Enum)"),
        ],
        default="N",
    )
    #
    default_action = StringField(
        choices=[
            ("R", "Raise Disposition Alarm"),
            ("C", "Clear Disposition Alarm"),
            ("I", "Ignore Disposition Alarm"),
            ("D", "Drop Event"),
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
        if self.vars_conditions:
            r["vars_conditions"] = [m.json_data for m in self.vars_conditions]
            r["vars_conditions_op"] = self.vars_conditions_op
        if self.update_oper_status != "N":
            r["update_oper_status"] = self.update_oper_status
        if self.replace_rule:
            r |= {
                "replace_rule__name": self.replace_rule.name,
                "replace_rule_policy": self.replace_rule_policy,
            }
        if self.object_actions:
            r["object_actions"] = {
                "interaction_audit": (
                    self.object_actions.interaction_audit.value
                    if self.object_actions.interaction_audit
                    else None
                ),
                "run_discovery": self.object_actions.run_discovery,
                "update_avail_status": self.object_actions.update_avail_status,
            }
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

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

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
    def get_actions(cls, event_class: Optional[EventClass] = None):
        """"""
        r = []
        for rule in DispositionRule.objects.filter(
            conditions__event_class_re=event_class.name,
            is_active=True,
        ).order_by("preference"):
            r.append(DispositionRule.get_rule_config(rule))
        return r

    @classmethod
    def get_rule_config(cls, rule: "DispositionRule") -> Dict[str, Any]:
        """Generate DataStream Config from rule"""
        if rule.replace_rule and rule.replace_rule_policy == "w":
            # Merge Rule ?
            return DispositionRule.get_rule_config(rule.replace_rule)
        r = {
            "name": rule.name,
            "is_active": rule.is_active,
            "preference": rule.preference,
            "alarm_class": rule.alarm_disposition.name if rule.alarm_disposition else None,
            "stop_processing": rule.stop_processing,
            # disposition_var_map
            "match_expr": {},
            "vars_match_expr": {},
            "event_classes": [],
            "action": "ignore",
        }
        if rule.default_action:
            r["action"] = {"R": "raise", "C": "clear", "I": "ignore", "D": "drop"}[
                rule.default_action
            ]
        if rule.notification_group:
            r |= {
                "notification_group": str(rule.notification_group.id),
                "subject_template": rule.subject_template,
            }
        if rule.combo_condition and rule.combo_event_classes:
            r["combo_condition"] = {
                "combo_condition": rule.combo_condition,
                "combo_window": rule.combo_window,
                "combo_count": rule.combo_count,
                "combo_event_classes": [str(ec.id) for ec in rule.combo_event_classes],
            }
        if rule.handlers:
            r["handlers"] = [str(h.handler) for h in rule.handlers]
        if rule.vars_conditions_op == "OR":
            r["vars_match_expr"] = {"$or": [c.get_match_expr() for c in rule.vars_conditions]}
        else:
            for c in rule.vars_conditions or []:
                r["vars_match_expr"] |= c.get_match_expr()
        if rule.object_actions:
            r["object_actions"] = {
                "interaction_audit": rule.object_actions.interaction_audit.value,
                "run_discovery": rule.object_actions.run_discovery,
                "update_avail_status": rule.object_actions.update_avail_status,
            }
        if rule.update_oper_status != "N":
            r["resource_oper_status"] = rule.update_oper_status
            # enum_state
        if not rule.conditions:
            return r
        elif len(rule.conditions) == 1:
            r["match_expr"] = rule.conditions[0].get_match_expr()
        else:
            r["match_expr"] = {"$or": [x.get_match_expr() for x in rule.conditions]}
        r["event_classes"] = [str(x.id) for x in rule.get_event_classes()]
        return r
