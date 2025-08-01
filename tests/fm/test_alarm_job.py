# ----------------------------------------------------------------------
# Test Alarm Job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.fm.enum import AlarmAction, ActionStatus
from noc.core.fm.request import AlarmActionRequest, ActionItem, ActionConfig
from noc.services.correlator.alarmjob import AlarmJob
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


def test_run_request(alarm, tt_system):
    """Test run request"""
    req = AlarmActionRequest(
        ctx=0,
        actions=[
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
    job = AlarmJob.from_request(req, alarm=alarm, dry_run=True, stub_tt_system=tt_system)
    job.run()


# test save state validation and save
# test repeat
# test repeat on error step
# test run on action log
# test on save_state
# test on update alarm_watch
# test condition
# check allowed actions permission (run_once), user
