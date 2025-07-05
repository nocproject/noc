# ---------------------------------------------------------------------
# AlarmRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, List, Union, Literal

# Third-party modules
from bson import ObjectId
import cachetools
from noc.core.tt.types import Action as CtxAction, TTAction
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    LongField,
    IntField,
    ReferenceField,
    EmbeddedDocumentField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.main.models.label import Label
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.main.models.timepattern import TimePattern
from noc.main.models.template import Template
from noc.aaa.models.user import User
from .alarmseverity import AlarmSeverity
from .ttsystem import TTSystem
from .alarmclass import AlarmClass
from .escalationprofile import EscalationProfile


id_lock = Lock()


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    alarm_class: AlarmClass = ReferenceField(AlarmClass)
    severity: AlarmSeverity = ReferenceField(AlarmSeverity, required=False)
    reference_rx = StringField()

    def __str__(self):
        return f'{", ".join(self.labels)}, {self.alarm_class or ""}/{self.reference_rx}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


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
            ("any", "Update any"),  # Update
            ("raise", "When raise alarm"),
            ("clear", "When clear alarm"),
        ],
    )
    delay: int = IntField(min_value=0, default=0, max_value=3600)
    match_ack: Literal["any", "ack", "unack"] = StringField(default="any")
    time_pattern: Optional["TimePattern"] = ForeignKeyField(TimePattern)
    min_severity: Optional["AlarmSeverity"] = ReferenceField(AlarmSeverity)
    action = StringField(
        choices=[
            ("create_tt", "Create TT"),
            ("notify", "Notification"),
            ("log", "Add Log"),
            ("ack", "Acknowledge"),  # Unack if not clear ?
            ("handler", "Handler"),
            ("subscribe", "Subscribe"),
            ("clear", "Clear Alarm"),
        ],
        required=True,
    )
    severity_action = StringField(choices=["set", "min", "max", "inc", "dec"])
    handler = PlainReferenceField(Handler)
    notification_group = ForeignKeyField(NotificationGroup, required=False)
    tt_system = ReferenceField(TTSystem, required=False)
    user = ReferenceField(User, required=False)
    severity: Optional[AlarmSeverity] = ReferenceField(AlarmSeverity, required=False)
    message: str = StringField(required=False)
    template: Optional["Template"] = ForeignKeyField(Template, required=False)
    allow_fail: bool = BooleanField(default=True)
    stop_processing: bool = BooleanField(default=False)
    # manually: bool = BooleanField(default=True)
    # Sync collection Default ?

    def __str__(self):
        return f"{self.when}: {self.action}"

    def get_action(self) -> "CtxAction":
        """"""
        action = TTAction(self.action)
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
        match action:
            case TTAction.CREATE_TT, TTAction.CLOSE_TT:
                a.key = str(self.tt_system.id)
            case TTAction.ACK, TTAction.SUBSCRIBE:
                a.key = str(self.user.id)
            case TTAction.NOTIFY:
                a.key = str(self.notification_group.id)
            case TTAction.LOG:
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
    match: List[Match] = ListField(EmbeddedDocumentField(Match))
    #
    groups: List[Group] = ListField(EmbeddedDocumentField(Group))
    #
    actions: List[Action] = ListField(EmbeddedDocumentField(Action))
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
    rule_action = StringField(
        choices=[
            ("continue", "Continue processed"),
            ("drop", "Drop Alarm"),
            ("rewrite", "Rewrite Alarm Class"),
        ],
        default="continue",
    )
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

    def is_match(self, alarm):
        if not self.match:
            return True
        lset = set(alarm.effective_labels)
        for match in self.match:
            # Match against labels
            if match.exclude_labels and set(match.exclude_labels).issubset(lset):
                continue
            if not set(match.labels).issubset(lset):
                continue
            # Match against alarm class
            if match.alarm_class and match.alarm_class != alarm.alarm_class:
                continue
            # Match severity
            if match.severity and match.severity != AlarmSeverity.get_severity(alarm.severity):
                continue
            return True

    @classmethod
    def get_by_alarm(cls, alarm) -> List["AlarmRule"]:
        r = []
        for ar in AlarmRule.objects.filter(is_active=True):
            if ar.is_match(alarm):
                r.append(ar)
        return r
