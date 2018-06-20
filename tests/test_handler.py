# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.handler unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import pytest
# NOC modules
from noc.core.handler import get_handler, _CCACHE


def my_simple_handler():
    return 1


def my_add_handler(x, y):
    return x + y


def my_cached_handler():
    pass


def test_simple_handler():
    h = get_handler("noc.tests.test_handler.my_simple_handler")
    assert h
    assert h() == 1


def test_add_handler():
    h = get_handler("noc.tests.test_handler.my_add_handler")
    assert h
    assert h(1, 2) == 3


def test_callable():
    h = get_handler(my_simple_handler)
    assert h
    assert h == my_simple_handler


def test_cache():
    name = "noc.tests.test_handler.my_cached_handler"
    assert (name,) not in _CCACHE
    h = get_handler(name)
    assert h
    assert (name,) in _CCACHE
    hh = get_handler(name)
    assert h == hh


def test_invalid_format():
    # Invalid format
    with pytest.raises(ImportError):
        get_handler("xxx")


def test_invalid_module():
    # Invalid module
    with pytest.raises(ImportError):
        get_handler("invalid.handler")


def test_invalid_attribute():
    # Invalid attribute
    with pytest.raises(ImportError):
        get_handler("noc.tests.test_handler.invalid_handler")
