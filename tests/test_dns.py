# ----------------------------------------------------------------------
# noc.core.dns tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.dns.encoding import from_idna, to_idna, is_idna


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (str("example.com"), False),
        (str("example.xn--p1ai"), True),
        (str("xn--e1afmkfd.xn--p1ai"), True),
    ],
)
def test_is_idna(input, expected):
    assert is_idna(input) == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (str("example.com"), str("example.com")),
        (str("example.xn--p1ai"), str("example.рф")),
        (str("xn--e1afmkfd.xn--p1ai"), str("пример.рф")),
    ],
)
def test_from_idna(input, expected):
    assert from_idna(input) == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (str("example.com"), str("example.com")),
        (str("example.рф"), str("example.xn--p1ai")),
        (str("пример.рф"), str("xn--e1afmkfd.xn--p1ai")),
    ],
)
def test_to_idna(input, expected):
    assert to_idna(input) == expected
