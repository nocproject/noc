# ----------------------------------------------------------------------
# Test noc.lib.escape
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.escape import fm_escape, fm_unescape


@pytest.mark.parametrize(("value", "expected"), [(b"ab\xffcd", "ab=FFcd")])
def test_fm_escape(value: bytes, expected: str) -> None:
    assert fm_escape(value) == expected


@pytest.mark.parametrize(("value", "expected"), [("ab=FFcd", b"ab\xffcd")])
def test_fm_unescape(value: str, expected: bytes) -> None:
    assert fm_unescape(value) == expected
