# ----------------------------------------------------------------------
# Test Alarm Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.fm.enum import AlarmAction, ActionStatus
from noc.core.fm.request import ActionConfig
from noc.services.correlator.alarmaction import AlarmActionRunner
from noc.services.correlator.alarmjob import Item
from noc.services.correlator.actionlog import ActionLog
from noc.aaa.models.user import User
from .utils import get_alarm_mock, get_tt_system_mock


@pytest.fixture(scope="module")
def alarm():
    return get_alarm_mock()


@pytest.fixture(scope="module")
def user():
    return User(username="test User", first_name="Test")


@pytest.fixture(scope="module")
def tt_system():
    return get_tt_system_mock()


@pytest.fixture(
    params=[
        ActionConfig(action=AlarmAction.LOG, subject="Test Message"),
        ActionConfig(action=AlarmAction.ACK),
        ActionConfig(action=AlarmAction.UN_ACK),
        ActionConfig(action=AlarmAction.SUBSCRIBE),
        ActionConfig(action=AlarmAction.CLEAR),
    ]
)
def action_config(request):
    return request.param


def test_alarm_action(alarm, action_config: ActionConfig, user):
    runner = AlarmActionRunner([Item.from_alarm(alarm=alarm)], dry_run=True)
    alarm_ctx = alarm.get_message_ctx()
    #
    aa = ActionLog.from_request(action_config, started_at=alarm.timestamp)
    aa.user = user
    r = runner.run_action(
        aa.action,
        **aa.get_ctx(alarm_ctx=alarm_ctx),
    )  # aa.get_ctx for job
    assert r.status == ActionStatus.SUCCESS
    # Check Alarm Attributes
    match action_config.action:
        case AlarmAction.LOG:
            assert len(runner.alarm_log) == 1
        case AlarmAction.ACK:
            assert alarm.ack_user == user.username
        case AlarmAction.UN_ACK:
            assert alarm.ack_user is None
        case AlarmAction.SUBSCRIBE:
            assert len(alarm.watchers) == 1
            assert alarm.watchers[0].key == str(user.id)


@pytest.fixture(
    params=[
        ActionConfig(
            action=AlarmAction.CREATE_TT,
            key="stub",
            subject="Test Message",
            login="id1",
            pre_reason="sc1",
        ),
        ActionConfig(
            action=AlarmAction.CREATE_TT,
            key="stub",
            subject="Test Message",
            login="id1",
            pre_reason="sc2",
        ),
        ActionConfig(
            action=AlarmAction.CREATE_TT,
            key="stub",
            subject="Test Message",
            login="id1",
            pre_reason="sc3",
        ),
        ActionConfig(
            action=AlarmAction.CLOSE_TT,
            key="stub",
            subject="Test Message",
            login="id1",
            pre_reason="sc4",
        ),
        ActionConfig(
            action=AlarmAction.CLOSE_TT,
            key="stub",
            subject="Test Message",
            login="id1",
            pre_reason="sc5",
        ),
    ]
)
def tt_action_config(request):
    return request.param


def test_escalation_action(alarm, tt_action_config: ActionConfig, tt_system):
    """"""
    # Scenario 1 - escalation with no error
    # Scenario 2 - escalation with error with retry
    # Scenario 3 - escalation with clear alarm
    # Scenario 4 - escalation with clear error
    # Scenario 5 - escalation group alarm
    runner = AlarmActionRunner([Item.from_alarm(alarm=alarm)], dry_run=True)
    alarm_ctx = alarm.get_message_ctx()
    #
    aa = ActionLog.from_request(
        tt_action_config, started_at=alarm.timestamp, stub_tt_system=tt_system
    )
    r = runner.run_action(
        aa.action,
        **aa.get_ctx(alarm_ctx=alarm_ctx),
    )  # aa.get_ctx for job
    match tt_action_config:
        case "sc1":
            assert r.status == ActionStatus.SUCCESS
            assert r.document_id == "id1"
        case "sc2":
            assert r.status == ActionStatus.WARNING
            assert r.document_id is None
        case "sc3":
            assert r.status == ActionStatus.FAILED
            assert r.document_id is None
        case "sc4":
            assert r.status == ActionStatus.SUCCESS
