# ----------------------------------------------------------------------
# Mock ActiveAlarm for Tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import datetime
import logging
from bson import ObjectId

# NOC modules
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.ttsystem import TTSystem
from noc.main.models.notificationgroup import NotificationGroup

logger = logging.getLogger(__name__)


class SegmentMock:
    id: str = ObjectId()
    name: str = "Test Segment"
    is_redundant: bool = False


class ObjectProfile:
    id: int = 2
    name: str = "Object Profile"
    weight = 2


class MOMock:
    id = 2
    name = "Test Object"
    object_profile = ObjectProfile()
    segment = SegmentMock()
    tt_queue = None
    escalator_shard = ""

    def can_escalate(self, depended=False, tt_system=None):
        return True


def get_alarm_class_mock(name):
    AlarmClass.config = property(lambda x: None)
    alarm_class = AlarmClass(
        id=ObjectId(),
        name=name,
        subject_template="Alarm Subject",
        body_template="Alarm Body",
    )
    return alarm_class


def get_alarm_mock() -> "ActiveAlarm":
    AlarmClass.config = property(lambda x: None)
    alarm_class = AlarmClass(
        id=ObjectId(),
        name="NOC | Managed Object | Ping Failed",
        subject_template="Alarm Subject",
        body_template="Alarm Body",
    )
    alarm = ActiveAlarm(
        id=ObjectId(),
        timestamp=datetime.datetime.now(),
        last_update=datetime.datetime.now(),
        managed_object=MOMock(),
        alarm_class=alarm_class,
        severity=1000,
        base_severity=1000,
        vars={},
        reference=b"xxxx",
        log=[],
    )
    alarm.safe_save = lambda: None
    alarm.save = lambda: None
    alarm.has_merged_downlinks = lambda: False
    return alarm


def get_tt_system_mock() -> "TTSystem":
    """Prepare TTSystem for test"""
    tt_system = TTSystem(
        id=ObjectId(),
        name="Stub TT System",
        is_active=True,
        handler="noc.services.escalator.tt.stub.StubTTSystem",
        promote_items="D",
        connection="https://stub",
    )
    tt_system.save = lambda: None
    return tt_system


def get_notification_group_mock() -> "NotificationGroup":
    """Prepare notification group for mock"""
    # Send error/send success
    ng = NotificationGroup(name="stub")
    ng.notify = lambda subject, body, link=None, attachments=None, **kwargs: None
    return ng
