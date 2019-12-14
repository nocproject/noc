# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.comp tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
import pytest

# NOC modules
from noc.core.comp import smart_bytes, smart_text

if six.PY3:

    def bin(s):
        return bytes(s, "utf-8")


else:

    def bin(s):
        return str(s)


@pytest.mark.parametrize(
    "input,expected",
    [
        (six.text_type("abc"), six.text_type("abc")),
        (bin("abc"), six.text_type("abc")),
        (0, six.text_type("0")),
        (0.0, six.text_type("0.0")),
        (True, six.text_type("True")),
        (False, six.text_type("False")),
        (None, six.text_type("None")),
    ],
)
def test_smart_text(input, expected):
    v = smart_text(input)
    assert isinstance(v, six.text_type)
    assert v == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (six.text_type("abc"), bin("abc")),
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
    assert isinstance(v, six.binary_type)
    assert v == expected
