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
    delay = IntField()
    ack = BooleanField(default=False)  # If acked alarm
    time_pattern: TimePattern = ForeignKeyField(TimePattern)
    min_severity: AlarmSeverity = ReferenceField(AlarmSeverity)
    #
    template: Template = ForeignKeyField(Template)
    notification_group: NotificationGroup = ForeignKeyField(NotificationGroup)
    # Acton
    wait_condition = BooleanField(default=False)
    create_tt = BooleanField(default=False)
    # Stop or continue to next rule
    stop_processing = BooleanField(default=False)

    # user
    # Group
    # wait_ack
    # stop
    # create_tt
    # repeat


class TTSystemItem(EmbeddedDocument):
    tt_system = ReferenceField(TTSystem)
    pre_reason = StringField()
    global_limit = IntField()
    max_escalation_retries = IntField(default=30)


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
    tt_system_config = EmbeddedDocumentListField(TTSystemItem)
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
    # set_labels ?
    telemetry_sample = IntField(default=0)
    delay = IntField()

    # Caches
    _id_cache = cachetools.TTLCache(maxsize=50, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(self, oid: Union[str, ObjectId]) -> Optional["EscalationProfile"]:
        return EscalationProfile.objects.filter(id=oid).first()

    def get_tt_system_config(self, tt_system) -> Dict[str, str]:
        return {}
