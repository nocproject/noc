# ----------------------------------------------------------------------
# Test noc.core.snmp.render
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.snmp.render import (
    render_bin,
    render_utf8,
    get_text_renderer,
    render_empty,
    render_mac,
    get_string_renderer,
)

DEFAULT_OID = "1.3.6"


@pytest.mark.parametrize(
    ("renderer", "oid", "value", "expected"),
    [
        # render_bin
        (render_bin, None, b"", b""),
        (render_bin, None, b"123", b"123"),
        # render_utf8
        (render_utf8, None, b"123", "123"),
        (render_utf8, None, b"\xd0\xb2\xd0\xbe\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81", "вопрос"),
        # get_text_renderer
        (
            get_text_renderer("utf-8"),
            None,
            b"\xd0\xb2\xd0\xbe\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81",
            "вопрос",
        ),
        (get_text_renderer("cp1251"), None, b"\xe2\xee\xef\xf0\xee\xf1", "вопрос"),
        # render_empty
        (render_empty, None, b"", ""),
        (render_empty, None, b"123", ""),
        # render_mac
        (render_mac, None, b"", ""),
        (render_mac, None, b"\x01\x02\x03", ""),
        (render_mac, None, b"\x01\x02\x03\x04\x05\x06\x07", ""),
        (render_mac, None, b"\x01\x02\x03\x04\x05\x06", "01:02:03:04:05:06"),
        (render_mac, None, b"\x01\x02\x03\x04\x15\xff", "01:02:03:04:15:FF"),
        # get_string_renderer
        (get_string_renderer(""), None, b"", ""),
        (get_string_renderer(""), None, b"123", ""),
        (get_string_renderer("text"), None, b"", "text"),
        (get_string_renderer("text"), None, b"text", "text"),
        (get_string_renderer("text"), None, b"123", "text"),
    ],
)
def test_renderer(renderer, oid, value, expected):
    assert renderer(oid or DEFAULT_OID, value) == expected
