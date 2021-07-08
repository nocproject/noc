# ----------------------------------------------------------------------
# Change tracker test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.change.policy import change_tracker, SimpleChangeTrackerPolicy


def test_change_tracker_stack():
    p1 = SimpleChangeTrackerPolicy()
    assert change_tracker.get_policy() is not p1
    change_tracker.push_policy(p1)
    assert change_tracker.get_policy() is p1
    p2 = SimpleChangeTrackerPolicy()
    assert change_tracker.get_policy() is not p2
    change_tracker.push_policy(p2)
    assert change_tracker.get_policy() is not p1
    assert change_tracker.get_policy() is p2
    assert change_tracker.pop_policy() is p2
    assert change_tracker.pop_policy() is p1
