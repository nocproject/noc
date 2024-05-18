# ---------------------------------------------------------------------
# EscalationProfile model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from typing import Optional, Union, List, Dict
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
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.timepattern import TimePattern
from noc.main.models.template import Template
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.alarmseverity import AlarmSeverity

id_lock = Lock()


class EscalationItem(EmbeddedDocument):
    # Delay part
    delay = IntField(min_value=0)
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
    # Acton
    notification_group: NotificationGroup = ForeignKeyField(NotificationGroup)
    create_tt = BooleanField(default=False)
    # TT System that create escalation, Device by default
    tt_system = ReferenceField(TTSystem, required=False)
    # Processed condition
    # wait_condition = BooleanField(default=False)
    wait_ack = BooleanField(default=False)  # Wait alarm Acknowledge
    # wait_approve = BooleanField(default=False) # Approved Escalation
    # Stop or continue to next rule
    stop_processing = BooleanField(default=False)

    # user
    # Group
    # wait_ack
    # stop
    # create_tt
    # repeat
    def __str__(self):
        return f"{self.delay}: {self.create_tt}/{self.template}"

    @property
    def action(self) -> Optional[str]:
        if self.create_tt:
            return "create_tt"
        elif self.notification_group:
            return "notification"
        return None

    def get_key(self, tt_system: Optional[str] = None) -> str:
        if self.action == "create_tt":
            return str(tt_system)
        if self.action == "notification":
            return str(self.notification_group)
        return ""


class TTSystemItem(EmbeddedDocument):
    tt_system = ReferenceField(TTSystem)
    pre_reason = StringField()
    login = StringField()
    global_limit = IntField()
    max_escalation_retries = IntField(default=30)

    def get_config(self) -> Dict[str, str]:
        return {
            "pre_reason": self.pre_reason,
            "max_escalation_retries": self.max_escalation_retries,
            "login": self.login,
        }


@on_delete_check(
    check=[
        ("fm.Escalation", "profile"),
    ]
)
class EscalationProfile(Document):
    meta = {"collection": "escalationprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    escalation_policy = EnumField(EscalationPolicy, default=EscalationPolicy.ROOT)
    #     choices=["never", "rootfirst", "root", "alwaysfirst", "always"], default="root"
    # )
    tt_system_config: List[TTSystemItem] = EmbeddedDocumentListField(TTSystemItem)
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
    # End condition
    # * Delay
    # * Repeat
    # * Alarm close (Event Close)
    # * Manual
    # * Close Alarm (after end)

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
    max_repeats = IntField(default=0)
    # set_labels ?
    telemetry_sample = IntField(default=0)
    delay = IntField()

    # Caches
    _id_cache = cachetools.TTLCache(maxsize=50, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["EscalationProfile"]:
        return EscalationProfile.objects.filter(id=oid).first()

    @property
    def is_wait_ack(self) -> bool:
        """
        Check Escalation Wait alarm acknowledge
        :return:
        """
        for item in self.escalations:
            if item.wait_ack:
                return True
        return False

    def get_tt_system_config(self, tt_system: TTSystem) -> Dict[str, str]:
        r = tt_system.get_config()
        for item in self.tt_system_config:
            if item.tt_system.id == tt_system.id:
                r |= item.get_config()
        return r
