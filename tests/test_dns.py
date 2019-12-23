# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.dns tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
import six

# NOC modules
from noc.core.dns.encoding import from_idna, to_idna, is_idna


@pytest.mark.parametrize(
    "input,expected",
    [
        (six.text_type("example.com"), False),
        (six.text_type("example.xn--p1ai"), True),
        (six.text_type("xn--e1afmkfd.xn--p1ai"), True),
    ],
)
def test_is_idna(input, expected):
    assert is_idna(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (six.text_type("example.com"), six.text_type("example.com")),
        (six.text_type("example.xn--p1ai"), six.text_type("example.рф")),
        (six.text_type("xn--e1afmkfd.xn--p1ai"), six.text_type("пример.рф")),
    ],
)
def test_from_idna(input, expected):
    assert from_idna(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (six.text_type("example.com"), six.text_type("example.com")),
        (six.text_type("example.рф"), six.text_type("example.xn--p1ai")),
        (six.text_type("пример.рф"), six.text_type("xn--e1afmkfd.xn--p1ai")),
    ],
)
def test_to_idna(input, expected):
    assert to_idna(input) == expected
