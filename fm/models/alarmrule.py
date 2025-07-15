# ---------------------------------------------------------------------
# AlarmRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, List, Union, Callable, Dict, Any

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
    ReferenceField,
    ObjectIdField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.fm.enum import AlarmAction
from noc.core.fm.request import ActionConfig
from noc.core.matcher import build_matcher
from noc.main.models.label import Label
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.main.models.template import Template
from noc.aaa.models.user import User
from noc.sa.models.action import Action as ObjectAction
from .alarmseverity import AlarmSeverity
from .alarmclass import AlarmClass
from .escalationprofile import EscalationProfile


id_lock = Lock()


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    resource_groups = ListField(ObjectIdField())
    alarm_class: AlarmClass = ReferenceField(AlarmClass)
    severity: AlarmSeverity = ReferenceField(AlarmSeverity, required=False)
    reference_rx = StringField()

    def __str__(self):
        return f'{", ".join(self.labels)}, {self.alarm_class or ""}/{self.reference_rx}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.resource_groups:
            r["service_groups"] = {"$all": [str(x) for x in self.resource_groups]}
        if self.alarm_class:
            r["alarm_class"] = {"$in": [str(self.alarm_class.id)]}
        if self.severity:
            r["severity"] = {"$gte": self.severity.severity}
        if self.reference_rx:
            r["reference_rx"] = {"$regex": self.reference_rx}
        return r


class Group(EmbeddedDocument):
    # Group Alarm reference Template
    reference_template = StringField(default="")
    # Group Alarm Class (Group by default)
    alarm_class = PlainReferenceField(AlarmClass, required=False)
    # Group Title template
    title_template = StringField(default="")
    # Minimum amount of alarms to create the group
    min_threshold = IntField(default=0, min_value=0)
    # Maximum amount of alarms to create the group
    max_threshold = IntField(default=1, min_value=0)
    # Correlation window in seconds to check min_threshold
    window = IntField(default=0, min_value=0)
    # Labels for set Group Alarm
    labels = ListField(StringField())

    def __str__(self):
        return f'{self.alarm_class or ""}/{self.title_template or ""}: {self.reference_template}'

    def get_config(self) -> Dict[str, Any]:
        """"""
        return {
            "reference_template": self.reference_template,
            "alarm_class": str(self.alarm_class.id) if self.alarm_class else None,
            "title_template": self.title_template,
            "min_threshold": self.min_threshold,
            "max_threshold": self.max_threshold,
            "window": self.window,
            "labels": list(self.labels),
        }


class Action(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    when = StringField(
        default="raise",
        choices=[
            ("update", "When Alarm Update"),  # Update
            ("raise", "When raise alarm"),
            ("clear", "When clear alarm"),
        ],
    )
    handler: Optional["Handler"] = PlainReferenceField(Handler, required=False)
    notification_group = ForeignKeyField(NotificationGroup, required=False)
    user: Optional["User"] = ForeignKeyField(User, required=False)
    template: Optional["Template"] = ForeignKeyField(Template, required=False)
    message: str = StringField(required=False)
    object_action: Optional["ObjectAction"] = ReferenceField(ObjectAction)
    # Run Diagnostic
    # script
    # allow_fail: bool = BooleanField(default=True) To check
    # manually: bool = BooleanField(default=True)
    # Sync collection Default ?

    def __str__(self):
        r = []
        if self.handler:
            r.append(f"H::{self.handler}")
        if self.notification_group:
            r.append(f"NG::{self.notification_group}")
        if self.user:
            r.append(f"U::{self.user.username}")
        if self.object_action:
            r.append(f"OA::{self.user.username}")
        return f"{self.when}: {';'.join(r)}"

    def get_config(self) -> List["ActionConfig"]:
        """Get AlarmAction Config"""
        r = []
        if self.handler:
            r.append(
                ActionConfig(
                    action=AlarmAction.HANDLER,
                    key=str(self.handler.handler),
                    template=str(self.template.id) if self.template else None,
                )
            )
        if self.notification_group:
            r.append(
                ActionConfig(
                    action=AlarmAction.NOTIFY,
                    key=str(self.notification_group.id),
                    template=str(self.template.id) if self.template else None,
                )
            )
        if self.user:
            r.append(
                ActionConfig(
                    action=AlarmAction.ACK,
                    key=str(self.user.id),
                    template=str(self.template.id) if self.template else None,
                )
            )
        return r


@bi_sync
class AlarmRule(Document):
    meta = {
        "collection": "alarmrules",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["match.labels", ("match.alarm_class", "match.labels")],
    }

    name = StringField(unique=True)
    description = StringField()
    is_active = BooleanField(default=True)
    #
    match: List[Match] = EmbeddedDocumentListField(Match)
    #
    groups: List[Group] = EmbeddedDocumentListField(Group)
    #
    actions: List[Action] = EmbeddedDocumentListField(Action)
    #
    escalation_profile: Optional[EscalationProfile] = ReferenceField(EscalationProfile)
    #
    severity_policy = StringField(
        choices=[
            ("B", "Base"),
            ("AB", "Affected Based Severity Preferred"),
            ("AL", "Affected Limit"),
            ("ST", "By Tokens"),
        ],
        default="AL",
    )
    min_severity: Optional[AlarmSeverity] = ReferenceField(AlarmSeverity, required=False)
    max_severity: Optional[AlarmSeverity] = ReferenceField(AlarmSeverity, required=False)
    # Set, Match, Increase, Severity
    # severity_policy = StringField(
    #     choices=["match", "set", "inc", "dec"], default="set"
    # )
    rule_action = StringField(
        choices=[
            ("continue", "Continue processed"),
            ("drop", "Drop Alarm"),
            ("rewrite", "Rewrite Alarm Class"),
        ],
        default="continue",
    )
    # checks
    alarm_class = PlainReferenceField(AlarmClass, required=False)
    stop_processing = BooleanField(default=False)
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
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["AlarmRule"]:
        return AlarmRule.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["AlarmRule"]:
        return AlarmRule.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["AlarmRule"]:
        return AlarmRule.objects.filter(bi_id=bi_id).first()

    def get_matcher(self) -> Callable:
        """"""
        expr = []
        for r in self.match:
            expr.append(r.get_match_expr())
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def is_match(self, alarm) -> bool:
        """Local Match rules"""
        matcher = self.get_matcher()
        ctx = alarm.get_matcher_ctx()
        return matcher(ctx)

    @classmethod
    def get_by_alarm(cls, alarm) -> List["AlarmRule"]:
        r = []
        for ar in AlarmRule.objects.filter(is_active=True):
            if ar.is_match(alarm):
                r.append(ar)
        return r

    @classmethod
    def get_config(cls, rule: "AlarmRule"):
        """Generate Rule config"""
        r = {
            "id": rule.id,
            "name": rule.name,
            "is_active": rule.is_active,
            "actions": [],
            "groups": [g.get_config() for g in rule.groups],
            "match_expr": [r.get_match_expr() for r in rule.match],
            "rule_action": rule.rule_action,
            "severity_policy": rule.severity_policy,
            "stop_processing": rule.stop_processing,
        }
        for a in rule.actions:
            r["actions"] += [cfg.model_dump() for cfg in a.get_config()]
        if rule.rule_action == "rewrite" and rule.alarm_class:
            r["rewrite_alarm_class"] = str(rule.alarm_class.id)
        elif rule.rule_action == "rewrite" and not rule.alarm_class:
            r["rule_action"] = "continue"
        if rule.min_severity:
            r["min_severity"] = rule.min_severity.severity
        if rule.max_severity:
            r["max_severity"] = rule.max_severity.severity
        return r
