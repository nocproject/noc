# ----------------------------------------------------------------------
# noc.core.comp tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.comp import smart_bytes, smart_text


def bin(s):
    return bytes(s, "utf-8")


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("abc", "abc"),
        (bin("abc"), "abc"),
        (0, "0"),
        (0.0, "0.0"),
        (True, "True"),
        (False, "False"),
        (None, "None"),
    ],
)
def test_smart_text(input, expected) -> None:
    v = smart_text(input)
    assert isinstance(v, str)
    assert v == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("abc", bin("abc")),
        (bin("abc"), bin("abc")),
        (0, bin("0")),
        (0.0, bin("0.0")),
        (True, bin("True")),
        (False, bin("False")),
        (None, bin("None")),
    ],
)
def test_smart_bytes(input, expected) -> None:
    v = smart_bytes(input)
    assert isinstance(v, bytes)
    assert v == expected
