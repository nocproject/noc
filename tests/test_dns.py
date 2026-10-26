# ----------------------------------------------------------------------
# noc.core.dns tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.dns.encoding import from_idna, is_idna, to_idna


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("example.com", False),
        ("example.xn--p1ai", True),
        ("xn--e1afmkfd.xn--p1ai", True),
    ],
)
def test_is_idna(input: str, expected: bool) -> None:
    assert is_idna(input) == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("example.com", "example.com"),
        ("example.xn--p1ai", "example.рф"),
        ("xn--e1afmkfd.xn--p1ai", "пример.рф"),
    ],
)
def test_from_idna(input: str, expected: str) -> None:
    assert from_idna(input) == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("example.com", "example.com"),
        ("example.рф", "example.xn--p1ai"),
        ("пример.рф", "xn--e1afmkfd.xn--p1ai"),
    ],
)
def test_to_idna(input: str, expected: str) -> None:
    assert to_idna(input) == expected
