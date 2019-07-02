# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test telnet module
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from six import StringIO

# NOC modules
from noc.core.script.cli.telnet import TelnetParser


@pytest.mark.parametrize(
    "scenario",
    [
        # Feed, Expected, Sent Expected
        # Feed - parser input
        # Expected - expected parser output
        # Sent Expected - expected control sequence output
        # Empty feed
        [("", "", "")],
        # Plain text
        [("Lorem ipsum", "Lorem ipsum", ""), ("dolor sit amet", "dolor sit amet", "")],
        # Escaped IAC
        [("Lorem\xff\xff ipsum", "Lorem\xff ipsum", ""), ("dolor sit amet", "dolor sit amet", "")],
        # Incomplete IAC
        [("Lorem ipsum\xff", "Lorem ipsum", ""), ("\xffdolor sit amet", "\xffdolor sit amet", "")],
        # Ignored commands
        [
            ("Lorem\xff\xf5 ipsum", "Lorem ipsum", ""),
            ("Lorem\xff\xf6 ipsum", "Lorem ipsum", ""),
            ("Lorem\xff", "Lorem", ""),
            ("\xf5ipsum", "ipsum", ""),
        ],
        # Accepted commands
        [
            # IAC DO ECHO -> IAC WILL ECHO
            ("\xff\xfd\x01Lorem ipsum", "Lorem ipsum", "\xff\xfb\x01"),
            # IAC DO SGA -> IAC WILL SGA
            ("\xff\xfd\x03Lorem ipsum", "Lorem ipsum", "\xff\xfb\x03"),
        ],
        # IAC DO
        [
            ("\xff\xfd\x01", "", "\xff\xfb\x01"),
            ("\xff\xfd\x02", "", "\xff\xfc\x02"),
            ("\xff\xfd\x03", "", "\xff\xfb\x03"),
            ("\xff\xfd\x04", "", "\xff\xfc\x04"),
            ("\xff\xfd\x18", "", "\xff\xfb\x18"),
            # NAWS
            ("\xff\xfd\x1f", "", "\xff\xfb\x1f\xff\xfa\x1f\x00\x80\x00\x80\xff\xf0"),
        ],
        # IAC DONT
        [("\xff\xfe\x01Lorem", "Lorem", "\xff\xfc\x01")],
        # IAC WONT
        [("\xff\xfc\x01Lorem", "Lorem", "\xff\xfe\x01")],
        # IAC WILL
        [
            ("\xff\xfb\x01", "", "\xff\xfd\x01"),
            ("\xff\xfb\x02", "", "\xff\xfe\x02"),
            ("\xff\xfb\x03", "", "\xff\xfd\x03"),
            ("\xff\xfb\x04", "", "\xff\xfe\x04"),
            ("\xff\xfb\x18", "", "\xff\xfd\x18"),
        ],
        # Invalid IAC
        [("\xff\x00Lorem ipsum", "orem ipsum", "")],
        # TTYPE
        [
            ("\xff\xfa\x18\x01\xff\xf0Lorem", "Lorem", "\xff\xfa\x18\x00XTERM\xff\xf0"),
            ("\xff\xfa\x18", "", ""),
            ("\x01\xff\xf0Lorem", "Lorem", "\xff\xfa\x18\x00XTERM\xff\xf0"),
        ],
    ],
)
def test_telnet_scenario(scenario):
    writer = StringIO()
    parser = TelnetParser(writer=writer.write)
    for feed, expected, sent_expected in scenario:
        data = parser.feed(feed)
        assert data == expected
        ctl = writer.getvalue()
        assert ctl == sent_expected
        writer.truncate(0)


@pytest.mark.parametrize(
    "data,expected",
    [
        ("", ""),
        ("12345", "12345"),
        ("\xfe12345", "\xfe12345"),
        ("\xff12345", "\xff\xff12345"),
        ("123\xff45", "123\xff\xff45"),
        ("12345\xff", "12345\xff\xff"),
    ],
)
def test_telnet_escape(data, expected):
    assert TelnetParser.escape(data) == expected


@pytest.mark.parametrize("cmd, opt, expected", [])
def test_telnet_iac_repr(cmd, opt, expected):
    assert TelnetParser.iac_repr(cmd, opt) == expected
