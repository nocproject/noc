# ----------------------------------------------------------------------
# Test Alarm Watchers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import pytest

# NOC modules
from noc.aaa.models.user import User
from noc.fm.models.alarmwatch import Effect
from .utils import get_alarm_mock


@pytest.fixture(scope="function")
def alarm():
    return get_alarm_mock()


@pytest.fixture(scope="module")
def user():
    return User(username="test User", first_name="Test")


def test_base_severity(alarm):
    """
    """
    severity = alarm.get_effective_severity()
    assert severity == 1000
    severity = alarm.get_effective_severity(severity=2000)
    assert severity == 2000


def test_limit_severity_severity(alarm):
    """
    """
    alarm.add_watch(Effect.SEVERITY, key="", max_severity=500)
    severity = alarm.get_effective_severity()
    assert severity == 500
    alarm.add_watch(Effect.SEVERITY, key="", min_severity=1500)
    severity = alarm.get_effective_severity()
    assert severity == 1500


# Policy
# Min/Max severity
# User change Based Severity
