# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.comp tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.comp import smart_bytes, smart_text, bord


def bin(s):
    return bytes(s, "utf-8")


@pytest.mark.parametrize(
    "input,expected",
    [
        (str("abc"), str("abc")),
        (bin("abc"), str("abc")),
        (0, str("0")),
        (0.0, str("0.0")),
        (True, str("True")),
        (False, str("False")),
        (None, str("None")),
    ],
)
def test_smart_text(input, expected):
    v = smart_text(input)
    assert isinstance(v, str)
    assert v == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (str("abc"), bin("abc")),
        (bin("abc"), bin("abc")),
        (0, bin("0")),
        (0.0, bin("0.0")),
        (True, bin("True")),
        (False, bin("False")),
        (None, bin("None")),
    ],
)
def test_smart_bytes(input, expected):
    v = smart_bytes(input)
    assert isinstance(v, bytes)
    assert v == expected


@pytest.mark.parametrize("input,expected", [(b"\x00", 0), (b"\x01", 1), (b"\x10", 16)])
def test_bord(input, expected):
    assert bord(input[0]) == expected
