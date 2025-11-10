# ----------------------------------------------------------------------
# SNMP TC tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.snmp.util import render_tc


@pytest.mark.parametrize(
    ("value", "base_type", "format", "expected"),
    [
        # Integer32 formatting
        (1234, "Integer32", None, "1234"),
        (1234, "Integer32", "x", "4d2"),
        (1234, "Integer32", "o", "2322"),
        (1234, "Integer32", "d", "1234"),
        (1234, "Integer32", "d-2", "12.34"),
        (1234, "Integer32", "d-4", "0.1234"),
        (1234, "Integer32", "d-6", "0.001234"),
        # OctetString formatting
        ("\x80", "OctetString", "1x", "80"),
        ("\x80\xff", "OctetString", "2x", "80ff"),
        ("\x01\x02\x03\x04", "OctetString", "1d:1d:1d:1d", "1:2:3:4"),
        ("\x80", "OctetString", "1d", "128"),
        ("\x80\xff", "OctetString", "2d", "33023"),
        ("\x80", "OctetString", "1o", "200"),
        ("\x04\x74\x65\x73\x74", "OctetString", "*1a", "test"),
        ("\x74\x65\x73\x74", "OctetString", "255a", "test"),
        ("UTF8", "OctetString", "255t", "UTF8"),
        ("abcdef", "OctetString", "1x:", "61:62:63:64:65:66"),
        (
            "\x07\xde\x02\x02\x03*\x0b\x01+\x01\x01",
            "OctetString",
            "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
            "2014-2-2,3:42:11.1,+1:1",
        ),
        (b"\x80", "OctetString", "1x", "80"),
        (b"\x80\xff", "OctetString", "2x", "80ff"),
        (b"\x01\x02\x03\x04", "OctetString", "1d:1d:1d:1d", "1:2:3:4"),
        (b"\x80", "OctetString", "1d", "128"),
        (b"\x80\xff", "OctetString", "2d", "33023"),
        (b"\x80", "OctetString", "1o", "200"),
        (b"\x04\x74\x65\x73\x74", "OctetString", "*1a", "test"),
        (b"\x74\x65\x73\x74", "OctetString", "255a", "test"),
        (b"UTF8", "OctetString", "255t", "UTF8"),
        (b"abcdef", "OctetString", "1x:", "61:62:63:64:65:66"),
        (
            b"\x07\xde\x02\x02\x03*\x0b\x01+\x01\x01",
            "OctetString",
            "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
            "2014-2-2,3:42:11.1,+1:1",
        ),
    ],
)
def test_render_tc(value, base_type, format, expected):
    assert render_tc(value, base_type, format) == expected
