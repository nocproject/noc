# ----------------------------------------------------------------------
#  Lock tests
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2021 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.lock.base import get_locked_items
from noc.core.lock.process import ProcessLock


def test_get_locked_items():
    assert get_locked_items() == set()
    lock = ProcessLock("test", "pytest")
    with lock.acquire(["r1", "r2", "r3"]):
        assert get_locked_items() == {"r1", "r2", "r3"}
    assert get_locked_items() == set()


def test_nested_locks():
    lock = ProcessLock("test", "pytest")
    with lock.acquire(["r1", "r2", "r3"]):
        with pytest.raises(RuntimeError):
            with lock.acquire(["r4", "r5"]):
                pass
