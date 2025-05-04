# ----------------------------------------------------------------------
# Test telnet module
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
import pytest
from io import BytesIO

# NOC modules
from noc.core.script.base import BaseScript
from noc.core.script.cli.base import BaseCLI
from noc.core.script.cli.telnet import TelnetStream
from noc.core.ioloop.util import IOLoopContext


class ScriptStub(BaseScript):
    name = "Generic.Host"

    def __init__(self):
        super().__init__(None, {})

    def interface(self):
        return


class ProfileStub(object):
    telnet_send_on_connect = None

    @classmethod
    def get_telnet_naws(cls) -> bytes:
        return b"\x00\x80\x00\x80"


class CLIStub(BaseCLI):
    def __init__(self):
        super().__init__(ScriptStub())
        self.tos = 0
        self.logger = logging.getLogger("CLIStub")
        self.profile = ProfileStub()


class MyTelnetStream(TelnetStream):
    def __init__(self):
        super().__init__(CLIStub())
        self.writer = BytesIO()

    async def write(self, data: bytes, raw: bool = False):
        if not raw:
            data = self.escape(data)
        self.writer.write(data)

    def get_write_buffer(self) -> bytes:
        data = self.writer.getvalue()
        self.writer = BytesIO()
        return data


@pytest.mark.parametrize(
    "scenario",
    [
        # Feed, Expected, Sent Expected
        # Feed - parser input
        # Expected - expected parser output
        # Sent Expected - expected control sequence output
        # Empty feed
        [(b"", b"", b"")],
        # Plain text
        [(b"Lorem ipsum", b"Lorem ipsum", b""), (b"dolor sit amet", b"dolor sit amet", b"")],
        # Escaped IAC
        [
            (b"Lorem\xff\xff ipsum", b"Lorem\xff ipsum", b""),
            (b"dolor sit amet", b"dolor sit amet", b""),
        ],
        # Incomplete IAC
        [
            (b"Lorem ipsum\xff", b"Lorem ipsum", b""),
            (b"\xffdolor sit amet", b"\xffdolor sit amet", b""),
        ],
        # Ignored commands
        [
            (b"Lorem\xff\xf5 ipsum", b"Lorem ipsum", b""),
            (b"Lorem\xff\xf6 ipsum", b"Lorem ipsum", b""),
            (b"Lorem\xff", b"Lorem", b""),
            (b"\xf5ipsum", b"ipsum", b""),
        ],
        # Accepted commands
        [
            # IAC DO ECHO -> IAC WILL ECHO
            (b"\xff\xfd\x01Lorem ipsum", b"Lorem ipsum", b"\xff\xfb\x01"),
            # IAC DO SGA -> IAC WILL SGA
            (b"\xff\xfd\x03Lorem ipsum", b"Lorem ipsum", b"\xff\xfb\x03"),
        ],
        # IAC DO
        [
            (b"\xff\xfd\x01", b"", b"\xff\xfb\x01"),
            (b"\xff\xfd\x02", b"", b"\xff\xfc\x02"),
            (b"\xff\xfd\x03", b"", b"\xff\xfb\x03"),
            (b"\xff\xfd\x04", b"", b"\xff\xfc\x04"),
            (b"\xff\xfd\x18", b"", b"\xff\xfb\x18"),
            # NAWS
            (b"\xff\xfd\x1f", b"", b"\xff\xfb\x1f\xff\xfa\x1f\x00\x80\x00\x80\xff\xf0"),
        ],
        # IAC DONT
        [(b"\xff\xfe\x01Lorem", b"Lorem", b"\xff\xfc\x01")],
        # IAC WONT
        [(b"\xff\xfc\x01Lorem", b"Lorem", b"\xff\xfe\x01")],
        # IAC WILL
        [
            (b"\xff\xfb\x01", b"", b"\xff\xfd\x01"),
            (b"\xff\xfb\x02", b"", b"\xff\xfe\x02"),
            (b"\xff\xfb\x03", b"", b"\xff\xfd\x03"),
            (b"\xff\xfb\x04", b"", b"\xff\xfe\x04"),
            (b"\xff\xfb\x18", b"", b"\xff\xfd\x18"),
        ],
        # Invalid IAC
        [(b"\xff\x00Lorem ipsum", b"orem ipsum", b"")],
        # TTYPE
        [
            (b"\xff\xfa\x18\x01\xff\xf0Lorem", b"Lorem", b"\xff\xfa\x18\x00XTERM\xff\xf0"),
            (b"\xff\xfa\x18", b"", b""),
            (b"\x01\xff\xf0Lorem", b"Lorem", b"\xff\xfa\x18\x00XTERM\xff\xf0"),
        ],
    ],
)
def test_telnet_scenario(scenario):
    stream = MyTelnetStream()
    for feed, expected, sent_expected in scenario:
        with IOLoopContext() as loop:
            data = loop.run_until_complete(stream.feed(feed))
        assert data == expected
        assert stream.get_write_buffer() == sent_expected


@pytest.mark.parametrize(
    "data,expected",
    [
        (b"", b""),
        (b"12345", b"12345"),
        (b"\xfe12345", b"\xfe12345"),
        (b"\xff12345", b"\xff\xff12345"),
        (b"123\xff45", b"123\xff\xff45"),
        (b"12345\xff", b"12345\xff\xff"),
    ],
)
def test_telnet_escape(data, expected):
    assert MyTelnetStream().escape(data) == expected


@pytest.mark.parametrize("cmd, opt, expected", [])
def test_telnet_iac_repr(cmd, opt, expected):
    assert MyTelnetStream().iac_repr(cmd, opt) == expected
