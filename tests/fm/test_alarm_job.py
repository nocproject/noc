# ----------------------------------------------------------------------
# Test Alarm Job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import datetime
import orjson
import pytest

# NOC modules
from noc.core.fm.enum import AlarmAction, ActionStatus
from noc.core.fm.request import AlarmActionRequest, ActionConfig
from noc.services.correlator.alarmjob import AlarmJob
from noc.aaa.models.user import User
from .utils import get_alarm_mock, get_tt_system_mock, get_notification_group_mock


@pytest.fixture
def alarm():
    return get_alarm_mock()


@pytest.fixture(scope="module")
def user():
    return User(username="test User", first_name="Test")


@pytest.fixture(scope="module")
def tt_system():
    return get_tt_system_mock()


@pytest.fixture(scope="module")
def notification_group():
    return get_notification_group_mock()


def test_run_request(alarm, user, tt_system):
    """Test run request, test condition"""
    req = AlarmActionRequest(
        ctx=0,
        actions=[
            ActionConfig(
                action=AlarmAction.ACK,
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
                pre_reason="sc1",
            ),
        ],
        start_at=alarm.timestamp,
    )
    job = AlarmJob.from_request(
        req,
        alarm=alarm,
        dry_run=True,
        stub_tt_system=tt_system,
        stub_user=user,
    )
    job.run()
    assert len(job.actions) == 3
    assert (
        all(
            a.status == ActionStatus.SUCCESS
            for a in job.actions
            if a.action != AlarmAction.CLOSE_TT
        )
        is True
    )
    # Test Items clear (is_end)
    # test on update alarm_watch


def test_state(alarm, user, tt_system):
    """test save state validation and save"""
    # Test State
    req = AlarmActionRequest(
        ctx=0,
        actions=[
            ActionConfig(
                action=AlarmAction.ACK,
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
                pre_reason="sc1",
            ),
        ],
        start_at=alarm.timestamp,
    )
    job = AlarmJob.from_request(
        req,
        alarm=alarm,
        dry_run=True,
        stub_tt_system=tt_system,
        stub_user=user,
    )
    state = job.save_state(dry_run=True)
    state.validate(clean=True)
    job.from_state(orjson.loads(state.to_json()), stub_alarms=[alarm])
    job.run()
    assert len(job.actions) == 3
    assert (
        all(
            a.status == ActionStatus.SUCCESS
            for a in job.actions
            if a.action != AlarmAction.CLOSE_TT
        )
        is True
    )


def test_repeat(alarm, notification_group):
    """test repeat, test repeat on error step"""
    req = AlarmActionRequest(
        ctx=0,
        actions=[
            ActionConfig(
                action=AlarmAction.LOG,
                key="stub",
                subject="Test Message",
            ),
            ActionConfig(
                delay=20,
                action=AlarmAction.ACK,
                key="stub",
                subject="Test Message",
            ),
        ],
        max_repeats=3,
        start_at=alarm.timestamp,
    )
    job = AlarmJob.from_request(
        req,
        alarm=alarm,
        dry_run=True,
    )
    job.run()
    assert len(job.actions) == 3
    assert job.actions[-1].status == ActionStatus.NEW
    assert job.actions[2].status == ActionStatus.NEW
    job.run()
    assert len(job.actions) == 3
    assert job.actions[-1].status == ActionStatus.NEW
    assert job.actions[2].status == ActionStatus.NEW
    ts = datetime.datetime.now() + datetime.timedelta(seconds=200)
    job.run(ts)
    assert len(job.actions) == 4
    assert job.actions[-1].status == ActionStatus.NEW
    assert job.actions[2].status == ActionStatus.SUCCESS
    # test repeat
    # test repeat on error step


def test_run_once(alarm, user, tt_system):
    """"""
    # not run_once if failed


# test run on action log
# test on update alarm_watch
# check allowed actions permission (run_once), user
