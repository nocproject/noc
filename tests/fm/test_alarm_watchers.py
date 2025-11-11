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
from .utils import get_alarm_mock, get_tt_system_mock, get_alarm_class_mock


@pytest.fixture
def alarm():
    return get_alarm_mock()


@pytest.fixture(scope="module")
def user():
    return User(username="test User", first_name="Test")


@pytest.fixture(scope="module")
def tt_system():
    return get_tt_system_mock()


@pytest.fixture
def alarm_class():
    return get_alarm_class_mock(name="System | Reboot")


def test_watchers_options(alarm):
    """
    Test watch API:
    * Add Watch
    * Remote Watch
    * Add With params
    """
    alarm.add_watch(Effect.HANDLER, key="noc.fm.handlers.alarm.stub.is_run_one")
    alarm.add_watch(Effect.HANDLER, key="noc.fm.handlers.alarm.stub.is_run_two", clear_only=True)
    alarm.add_watch(Effect.HANDLER, key="noc.fm.handlers.alarm.stub.is_run_three", immediate=True)
    alarm.touch_watch()
    assert alarm._run_handler == "run_one"
    alarm.touch_watch(is_clear=True)
    assert alarm._run_handler == "run_two"
    alarm.stop_watch(Effect.HANDLER, key="noc.fm.handlers.alarm.stub.is_run_two")
    alarm.touch_watch(is_clear=True)
    assert alarm._run_handler == "run_one"
    alarm.add_watch(Effect.CLEAR_ALARM, key="", immediate=True)
    with pytest.raises(ValueError):
        alarm.add_watch(Effect.CLEAR_ALARM, key="", once=True)
    with pytest.raises(ValueError):
        alarm.add_watch(Effect.CLEAR_ALARM, key="", clear_only=True)


def test_watchers_stop_clear(alarm):
    """Clear Alarm watchers"""
    assert alarm.allow_clear is True
    alarm.add_watch(Effect.STOP_CLEAR, key="")
    assert alarm.allow_clear is False
    r = alarm.clear_alarm("Test Clear", dry_run=True)
    assert r is None
    alarm.stop_watch(Effect.STOP_CLEAR, key="")
    r = alarm.clear_alarm("Test Clear", dry_run=True)
    assert r.status == "C"


def test_subscribe(alarm, user):
    """Subscribe method"""
    alarm.subscribe(user)
    w = alarm.watchers[0]
    assert w.effect == Effect.SUBSCRIPTION and w.key == str(user.id)
    alarm.unsubscribe(user)
    assert len(alarm.watchers) == 0


def test_escalation(alarm):
    """Escalate method"""
    tt_id_1 = "Stub:1"
    alarm.escalate(tt_id_1)
    w = alarm.watchers[0]
    assert len(alarm.watchers) == 1
    assert w.effect == Effect.TT_SYSTEM and w.key == tt_id_1 and not w.clear_only and w.immediate
    # two
    tt_id_2 = "Stub:2"
    alarm.escalate(tt_id_2, close_tt=True)
    w = alarm.watchers[1]
    assert len(alarm.watchers) == 2
    assert w.effect == Effect.TT_SYSTEM and w.key == tt_id_2 and w.clear_only and not w.immediate


def test_wait_tt(alarm):
    """
    Wait TT Scenario:
    * escalate with wait_tt param, set Disable Clear Alarm
    * run clear_alarm with force - set alarm clear
    """
    tt_id_1 = "Stub:1"
    alarm.escalate(tt_id_1, wait_tt=tt_id_1)
    r = alarm.clear_alarm("Test Clear", dry_run=True)
    assert r is None
    r = alarm.clear_alarm("Test Clear", force=True, dry_run=True)
    assert r.status == "C"


def test_alarm_clear_recursion(alarm):
    """Test run CLEAR_ALARM watch on clear_alarm method"""
    alarm.add_watch(Effect.CLEAR_ALARM, key="")
    r = alarm.clear_alarm("Test Clear", dry_run=True)
    assert r.status == "C"


def test_alarm_after(alarm):
    """
    After watchers. Execute watcher after deadline
    """
    # Add after watch - set wait_ts attribute
    now = datetime.datetime.now() + datetime.timedelta(hours=1)
    alarm.add_watch(Effect.CLEAR_ALARM, key="", after=now)
    assert alarm.wait_ts == now
    alarm.touch_watch()
    # Repeat add after watch - update after
    now = datetime.datetime.now() - datetime.timedelta(hours=1)
    alarm.add_watch(Effect.CLEAR_ALARM, key="", after=now)
    assert alarm.wait_ts == now
    # Do not Run CLEAR_ALARM effect on clear alarm
    alarm.touch_watch(is_clear=True)
    assert alarm.status == "A"
    alarm.touch_watch(dry_run=True)
    assert alarm.status == "C"
    # Remove After watch - clean wait_ts
    alarm.stop_watch(Effect.CLEAR_ALARM, key="")
    assert alarm.wait_ts is None


def test_rewrite_alarm_class(alarm, alarm_class):
    """
    Test rewrite AlarmClass
    """
    assert alarm.alarm_class.allow_rewrite(alarm_class)
    alarm.add_watch(Effect.REWRITE_ALARM_CLASS, key="", alarm_class=alarm_class)
    alarm.watchers[0].args["alarm_class"] = alarm_class
    alarm.touch_watch(dry_run=True)
    assert alarm.alarm_class != alarm_class
