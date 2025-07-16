# ---------------------------------------------------------------------
# EscalationProfile model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from typing import Optional, Union, List, FrozenSet
from threading import Lock

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    ReferenceField,
    EmbeddedDocumentListField,
    BooleanField,
    EnumField,
)
from bson import ObjectId
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.mongo.fields import ForeignKeyField
from noc.core.models.escalationpolicy import EscalationPolicy
from noc.core.tt.types import TTSystemConfig, EscalationMember
from noc.core.fm.enum import AlarmAction
from noc.core.fm.request import AlarmActionRequest, ActionConfig, AllowedAction, ActionItem
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.timepattern import TimePattern
from noc.main.models.template import Template
from noc.aaa.models.user import User
from noc.aaa.models.group import Group
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.activealarm import ActiveAlarm

id_lock = Lock()


class EscalationItem(EmbeddedDocument):
    """
    Escalation chain step config
    Attributes:
        delay: step start after start escalation time
    """

    meta = {"strict": False}
    # Delay part
    delay = IntField(min_value=0)
    # Processed condition
    alarm_ack = StringField(
        choices=[
            ("ack", "Alarm Acknowledge"),
            ("nack", "Alarm not Acknowledge"),
            ("any", "Any Acknowledge"),
        ],
        default="any",
    )
    time_pattern: TimePattern = ForeignKeyField(TimePattern)
    min_severity: AlarmSeverity = ReferenceField(AlarmSeverity)
    #
    template: Template = ForeignKeyField(Template)
    #
    close_template: Template = ForeignKeyField(Template)
    # Acton
    # Notification: Group, Register, Local
    notification_group: NotificationGroup = ForeignKeyField(NotificationGroup)
    register_message = BooleanField(default=False)
    # TT System Action
    create_tt = BooleanField(default=False)
    tt_queue: str = StringField(required=False)
    # TT System that create escalation, Device by default
    tt_system: Optional[TTSystem] = ReferenceField(TTSystem, required=False)
    # Repeat escalation
    repeat = BooleanField(default=False)
    # Subscribe
    # Assigned - User, From Contacts: Config, Local
    assigned_user: Optional[User] = ForeignKeyField(User, required=False)
    ack_policy: str = StringField(
        choices=[
            ("D", "Disable"),
            ("U", "UnAck"),
            ("A", "Ack User"),
            ("S", "Ack Subscriber"),
        ],
        default="D",
    )
    # wait_ack = BooleanField(default=False)  # Wait alarm Acknowledge
    # wait_condition = BooleanField(default=False)
    # wait_approve = BooleanField(default=False) # Approved Escalation
    # Stop or continue to next rule
    stop_processing = BooleanField(default=False)

    def __str__(self):
        return f"{self.delay}: {self.create_tt}/{self.template}"

    @property
    def member(self) -> Optional[EscalationMember]:
        if self.create_tt:
            return EscalationMember.TT_SYSTEM
        elif self.notification_group:
            return EscalationMember.NOTIFICATION_GROUP
        return None

    def get_key(self, tt_system: Optional[str] = None) -> str:
        if self.member == EscalationMember.TT_SYSTEM:
            tt_system = tt_system or self.tt_system.id
            return str(tt_system)
        if self.member == EscalationMember.NOTIFICATION_GROUP:
            return str(self.notification_group.id)
        return ""

    def get_config(
        self,
        tt_loging: Optional[str] = None,
        pre_reason: Optional[str] = None,
        promote_item: Optional[str] = None,
    ) -> List["ActionConfig"]:
        """"""
        r = []
        if self.notification_group:
            r += [
                ActionConfig(
                    delay=self.delay,
                    action=AlarmAction.NOTIFY,
                    key=str(self.notification_group.id),
                    template=str(self.template.id) if self.template else None,
                    ack=self.alarm_ack if self.alarm_ack != "nack" else "unack",
                    min_severity=self.min_severity.severity if self.min_severity else None,
                    time_pattern=self.time_pattern.time_pattern if self.time_pattern else None,
                    allow_fail=True,
                )
            ]
        if self.create_tt and self.tt_system:
            r.append(
                ActionConfig(
                    delay=self.delay,
                    action=AlarmAction.CREATE_TT,
                    key=str(self.tt_system.id),
                    template=str(self.template.id) if self.template else None,
                    ack=self.alarm_ack if self.alarm_ack != "nack" else "unack",
                    min_severity=self.min_severity.severity if self.min_severity else None,
                    time_pattern=self.time_pattern.time_pattern if self.time_pattern else None,
                    allow_fail=True,
                    pre_reason=pre_reason,
                    login=tt_loging,
                    queue=self.tt_queue,
                    promote_item_policy=promote_item,
                )
            )
        if self.register_message:
            r.append(
                ActionConfig(
                    delay=self.delay,
                    action=AlarmAction.REGISTER_MESSAGE,
                    template=str(self.template.id) if self.template else None,
                    ack=self.alarm_ack if self.alarm_ack != "nack" else "unack",
                    min_severity=self.min_severity.severity if self.min_severity else None,
                    time_pattern=self.time_pattern.time_pattern if self.time_pattern else None,
                    allow_fail=True,
                )
            )
        if self.ack_policy == "U":
            r.append(
                ActionConfig(
                    delay=self.delay,
                    action=AlarmAction.UN_ACK,
                    template=str(self.template.id) if self.template else None,
                    ack=self.alarm_ack if self.alarm_ack != "nack" else "unack",
                    min_severity=self.min_severity.severity if self.min_severity else None,
                    time_pattern=self.time_pattern.time_pattern if self.time_pattern else None,
                    allow_fail=True,
                )
            )
        elif self.ack_policy == "A" and self.assigned_user:
            r.append(
                ActionConfig(
                    delay=self.delay,
                    action=AlarmAction.ACK,
                    key=str(self.assigned_user.id),
                    template=str(self.template.id) if self.template else None,
                    ack=self.alarm_ack if self.alarm_ack != "nack" else "unack",
                    min_severity=self.min_severity.severity if self.min_severity else None,
                    time_pattern=self.time_pattern.time_pattern if self.time_pattern else None,
                    allow_fail=True,
                )
            )
        return r


class TTSystemItem(EmbeddedDocument):
    meta = {"strict": False}
    tt_system = ReferenceField(TTSystem)
    pre_reason = StringField()
    login = StringField()
    global_limit = IntField()
    max_escalation_retries = IntField(default=30)


class EscalationAction(EmbeddedDocument):
    meta = {"strict": False}
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)
    ack = BooleanField(default=False)
    close = BooleanField(default=False)
    log = BooleanField(default=False)
    subscribe = BooleanField(default=False)

    def get_config(self) -> List[AllowedAction]:
        """"""
        r = []
        if self.ack:
            r.append(AllowedAction(action=AlarmAction.ACK))
        if self.close:
            r.append(AllowedAction(action=AlarmAction.CLEAR))
        if self.subscribe:
            r.append(AllowedAction(action=AlarmAction.SUBSCRIBE))
        return r


@on_delete_check(
    check=[
        ("fm.Escalation", "profile"),
        ("fm.AlarmRule", "escalation_profile"),
    ]
)
class EscalationProfile(Document):
    """
    Description Escalation chain
    Attributes:
        end_condition: Condition when escalation ended.
            * Delay
            * Repeat
            * Alarm close (Event Close)
            * Manual
            * Close Alarm (after end)
    """

    meta = {"collection": "escalationprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    escalation_policy = EnumField(EscalationPolicy, default=EscalationPolicy.ROOT)
    #     choices=["never", "rootfirst", "root", "alwaysfirst", "always"], default="root"
    # )
    tt_system_config: List[TTSystemItem] = EmbeddedDocumentListField(TTSystemItem)
    actions: List[EscalationAction] = EmbeddedDocumentListField(EscalationAction)
    maintenance_policy = StringField(choices=["w", "i", "e"], default="end")
    alarm_consequence_policy = StringField(
        required=True,
        choices=[
            ("D", "Disable"),
            ("a", "Escalate with alarm timestamp"),
            ("c", "Escalate with current timestamp"),
        ],
        default="a",
    )
    end_condition = StringField(
        required=True,
        choices=[
            ("CR", "Close Root"),
            ("CA", "Close All"),
            ("E", "End Chain"),
            ("CT", "Close TT"),  # By Adapter
            ("M", "Manual"),  # By Adapter
        ],
        default="a",
    )
    # Close alarm after End
    close_alarm = BooleanField(default=False)
    escalations: List[EscalationItem] = EmbeddedDocumentListField(EscalationItem)  # Chain
    repeat_escalations = StringField(
        choices=[
            ("N", "Newer"),
            ("S", "Severity Change"),
            ("D", "After delay"),
        ],
        default="N",
    )
    repeat_delay = IntField(default=60)
    # set_labels ?
    telemetry_sample = IntField(default=0)

    # Caches
    _id_cache = cachetools.TTLCache(maxsize=50, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["EscalationProfile"]:
        return EscalationProfile.objects.filter(id=oid).first()

    def get_actions(
        self,
        user: Optional[User] = None,
        group: Optional[Group] = None,
    ) -> FrozenSet[AlarmAction]:
        """
        Getting TT System Action support

        Args:
            user:
            group:
        """
        r = []
        for a in self.actions:
            if user and user != a.user:
                # Group
                continue
            if group and group != a.group:
                continue
            if a.ack:
                r += [AlarmAction.ACK, AlarmAction.UN_ACK]
            if a.close:
                r.append(AlarmAction.CLEAR)
        return frozenset(r)

    def get_tt_system_config(self, tt_system: TTSystem) -> TTSystemConfig:
        r = tt_system.get_config()
        for item in self.tt_system_config:
            if item.tt_system.id != tt_system.id:
                continue
            if item.login:
                r.login = item.login
            if item.global_limit:
                r.global_limit = item.global_limit
            if item.max_escalation_retries:
                r.max_escalation_retries = item.max_escalation_retries
            if item.pre_reason:
                r.pre_reason = item.pre_reason
            break
        return r

    @property
    def alarm_wait_ended(self) -> bool:
        """Alarm must wait escalation ended before close"""
        return self.end_condition == "CT" or self.end_condition == "M"

    def from_alarm(self, alarm: ActiveAlarm):
        """"""
        actions = []
        for e in self.escalations:
            if e.tt_system:
                cfg = self.get_tt_system_config(e.tt_system)
                actions += e.get_config(tt_loging=cfg.login, pre_reason=cfg.pre_reason)
            else:
                actions += e.get_config()
        ma = []
        for a in self.actions:
            ma += a.get_config()
        req = AlarmActionRequest(
            item=ActionItem(alarm=str(alarm.id)),
            start_at=alarm.timestamp,
            actions=actions,
            allowed_actions=ma,
        )
        return req
