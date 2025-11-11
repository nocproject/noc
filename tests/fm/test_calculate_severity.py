# ----------------------------------------------------------------------
# Test calculate alarm severity
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.aaa.models.user import User
from noc.fm.models.alarmwatch import Effect
from .utils import get_alarm_mock


@pytest.fixture
def alarm():
    return get_alarm_mock()


@pytest.fixture(scope="module")
def user():
    return User(username="test User", first_name="Test")


def test_base_severity(alarm):
    """
    Change based severity
    """
    severity = alarm.get_effective_severity()
    assert severity == 1000
    severity = alarm.get_effective_severity(severity=2000)
    assert severity == 2000


def test_limit_severity_severity(alarm):
    """
    Test Limit min/max severity
    Set User Severity
    """
    alarm.add_watch(Effect.SEVERITY, key="", max_severity=500)
    severity = alarm.get_effective_severity()
    assert severity == 500
    alarm.stop_watch(Effect.SEVERITY, key="")
    alarm.add_watch(Effect.SEVERITY, key="", min_severity=1500)
    severity = alarm.get_effective_severity()
    assert severity == 1500


def test_severity_policies(alarm):
    """
    Test severity policies
    """
    # By summary
    # severity = alarm.get_effective_severity(policy="AB", summary={})
    # By Token
    alarm.effective_labels = ["noc::severity::warning"]
    severity = alarm.get_effective_severity(policy="ST")
    assert severity == 2000
