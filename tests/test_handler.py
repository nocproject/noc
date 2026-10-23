# ----------------------------------------------------------------------
# noc.core.handler unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import pytest

# NOC modules
from noc.core.handler import get_handler


def my_simple_handler():
    return 1


def my_add_handler(x, y):
    return x + y


def my_cached_handler():
    pass


def test_simple_handler() -> None:
    h = get_handler(f"{__name__}.my_simple_handler")
    assert h
    assert h() == 1


def test_add_handler() -> None:
    h = get_handler(f"{__name__}.my_add_handler")
    assert h
    assert h(1, 2) == 3


def test_callable() -> None:
    h = get_handler(my_simple_handler)
    assert h
    assert h == my_simple_handler


def test_invalid_format() -> None:
    # Invalid format
    with pytest.raises(ValueError):
        get_handler("xxx")


def test_invalid_module() -> None:
    # Invalid module
    with pytest.raises(ImportError):
        get_handler("invalid.handler")


def test_invalid_attribute() -> None:
    # Invalid attribute
    with pytest.raises(ImportError):
        get_handler(f"{__name__}.invalid_handler")
