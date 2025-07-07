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
        return r


class Group(EmbeddedDocument):
    # Group Alarm reference Template
    reference_template = StringField(default="")
    # Group Alarm Class (Group by default)
    alarm_class = PlainReferenceField(AlarmClass)
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


class Action(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    when = StringField(
        default="raise",
        choices=[
            ("both", "Update any"),  # Update
            ("raise", "When raise alarm"),
            ("clear", "When clear alarm"),
        ],
    )
    handler = PlainReferenceField(Handler)
    notification_group = ForeignKeyField(NotificationGroup, required=False)
    user = ForeignKeyField(User, required=False)
    template: Optional["Template"] = ForeignKeyField(Template, required=False)
    message: str = StringField(required=False)
    object_action = ReferenceField(ObjectAction)
    # script
    # allow_fail: bool = BooleanField(default=True) To check
    # manually: bool = BooleanField(default=True)
    # Sync collection Default ?

    def __str__(self):
        return f"{self.when}: {self.action}"

    def get_action(self) -> "CtxAction":
        """"""
        a = CtxAction(
            delay=self.delay,
            action=action,
            ack=self.match_ack,
            when={"any": "any", "raise": "on_start", "clear": "on_end"}[self.when],
            min_severity=self.min_severity.id if self.min_severity else None,
            max_retries=1,
            allow_fail=self.allow_fail,
            stop_processing=self.stop_processing,
        )
        match self.action:
            case AlarmAction.ACK, AlarmAction.SUBSCRIBE:
                a.key = str(self.user.id)
            case AlarmAction.NOTIFY:
                a.key = str(self.notification_group.id)
            case AlarmAction.LOG:
                a.key = self.message
        if self.time_pattern:
            a.time_pattern = self.time_pattern.time_pattern
        if self.template:
            a.template = str(self.template.id)
        return a


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
            ("CB", "Class Based Policy"),
            ("AB", "Affected Based Severity Preferred"),
            ("AL", "Affected Limit"),
            ("ST", "By Tokens"),
        ],
        default="AL",
    )
    # Set, Match, Increase, Severity
    # severity_action = StringField(choices=["set", "min", "max", "inc", "dec"])
    # severity: Optional[AlarmSeverity] = ReferenceField(AlarmSeverity, required=False)
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

    def is_match(self, o) -> bool:
        """Local Match rules"""
        matcher = self.get_matcher()
        ctx = o.get_matcher_ctx()
        return matcher(ctx)

    # def is_match(self, alarm):
    #     if not self.match:
    #         return True
    #     lset = set(alarm.effective_labels)
    #     for match in self.match:
    #         # Match against labels
    #         if match.exclude_labels and set(match.exclude_labels).issubset(lset):
    #             continue
    #         if not set(match.labels).issubset(lset):
    #             continue
    #         # Match against alarm class
    #         if match.alarm_class and match.alarm_class != alarm.alarm_class:
    #             continue
    #         # Match severity
    #         if match.severity and match.severity != AlarmSeverity.get_severity(alarm.severity):
    #             continue
    #         return True

    @classmethod
    def get_by_alarm(cls, alarm) -> List["AlarmRule"]:
        r = []
        ctx = alarm.get_ctx()
        for ar in AlarmRule.objects.filter(is_active=True):
            if ar.is_match(alarm):
                r.append(ar)
        return r

    @classmethod
    def get_config(cls, rule: "AlarmRule"):
        """Generate Rule config"""
        r = {}
        return r
