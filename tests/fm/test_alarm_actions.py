# ----------------------------------------------------------------------
# Test Alarm Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import datetime
import logging
from bson import ObjectId

# NOC modules
from noc.core.fm.enum import AlarmAction, ActionStatus
from noc.core.fm.request import ActionConfig
from noc.fm.models.activealarm import ActiveAlarm
from noc.services.correlator.alarmaction import AlarmActionRunner
from noc.services.correlator.alarmjob import Item
from noc.services.correlator.actionlog import ActionLog
from noc.aaa.models.user import User

logger = logging.getLogger(__name__)


class SegmentMock:
    id: str = ObjectId()
    name: str = "Test Segment"
    is_redundant: bool = False


class MOMock:
    id = 2
    name = "Test Object"
    segment = SegmentMock()


class AlarmClassMock:
    id = ObjectId()
    name = "NOC | Managed Object | Ping Failed"


alarm = ActiveAlarm(
    id=ObjectId(),
    timestamp=datetime.datetime.now(),
    last_update=datetime.datetime.now(),
    managed_object=MOMock(),
    alarm_class=AlarmClassMock(),
    severity=1000,
    base_severity=1000,
    vars={},
    reference=b"xxxx",
    log=[],
)
alarm.safe_save = lambda: None
alarm.save = lambda: None


def test_alar_action_notify():
    items = [Item(alarm=alarm)]
    runner = AlarmActionRunner(items, logger=logger)
    alarm_ctx = alarm.get_message_ctx()
    cfg = ActionConfig(action=AlarmAction.LOG, subject="Test Message")
    aa = ActionLog.from_request(cfg, started_at=alarm.timestamp)
    r = runner.run_action(
        aa.action,
        **aa.get_ctx(
            document_id=aa.document_id,
            alarm_ctx=alarm_ctx,
        ),
    )  # aa.get_ctx for job
    assert len(runner.alarm_log) == 1
    assert r.status == ActionStatus.SUCCESS


def test_alarm_action_ack():
    """"""
    user = User(username="test User", first_name="Test")
    items = [Item(alarm=alarm)]
    runner = AlarmActionRunner(items, logger=logger)
    alarm_ctx = alarm.get_message_ctx()
    aa = ActionLog(
        action=AlarmAction.ACK,
        key="",
        subject="Test Message",
        timestamp=alarm.timestamp,
        user=user,
    )
    r = runner.run_action(
        aa.action,
        **aa.get_ctx(
            document_id=aa.document_id,
            alarm_ctx=alarm_ctx,
        ),
    )  # aa.get_ctx for job
    assert r.status == ActionStatus.SUCCESS
    assert alarm.ack_user == user.username
    aa = ActionLog(
        action=AlarmAction.UN_ACK,
        key="",
        subject="Test Message",
        timestamp=alarm.timestamp,
        user=user,
    )
    r = runner.run_action(
        aa.action,
        **aa.get_ctx(
            document_id=aa.document_id,
            alarm_ctx=alarm_ctx,
        ),
    )  # aa.get_ctx for job
    assert r.status == ActionStatus.SUCCESS
    assert alarm.ack_user is None


def test_alarm_action_subscribe():
    """"""
    user = User(username="test User", first_name="Test")
    items = [Item(alarm=alarm)]
    runner = AlarmActionRunner(items, logger=logger)
    alarm_ctx = alarm.get_message_ctx()
    aa = ActionLog(
        action=AlarmAction.SUBSCRIBE,
        key="",
        subject="Test Message",
        timestamp=alarm.timestamp,
        user=user,
    )
    r = runner.run_action(
        aa.action,
        **aa.get_ctx(
            document_id=aa.document_id,
            alarm_ctx=alarm_ctx,
        ),
    )  # aa.get_ctx for job
    assert r.status == ActionStatus.SUCCESS
    assert len(alarm.watchers) == 1
    assert alarm.watchers[0].key == str(user.id)
