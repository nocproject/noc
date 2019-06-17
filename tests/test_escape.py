# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test noc.lib.escape
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.lib.escape import fm_escape, fm_unescape, json_escape


@pytest.mark.parametrize("value,expected", [
    ("ab\xffcd", "ab=FFcd")
])
def test_fm_escape(value, expected):
    assert fm_escape(value) == expected


@pytest.mark.parametrize("value,expected", [
    ("ab=FFcd", "ab\xffcd")
])
def test_fm_unescape(value, expected):
    assert fm_unescape(value) == expected

