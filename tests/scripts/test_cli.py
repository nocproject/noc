# ----------------------------------------------------------------------
# CLI testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import socket

# Third-party modules
import pytest

# NOC modules
from noc.core.script.base import BaseScript
from noc.core.script.cli.error import CLIConnectionRefused, CLIAuthFailed
from noc.sa.interfaces.igetdict import IGetDict
from noc.config import config

SSHD_HOST = config.tests.sshd_host
SSHD_PORT = config.tests.sshd_port
DROPBEAR_HOST = config.tests.dropbear_host
DROPBEAR_PORT = config.tests.dropbear_port
TELNETD_HOST = config.tests.telnetd_host
TELNETD_PORT = config.tests.telnetd_port
TEST_USER = "test"
TEST_PW = "pw1234567890"
BROKEN_USER = TEST_USER + "X"
BROKEN_PW = TEST_PW + "X"


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool="default"):
        self.config = self.ServiceConfig(pool=pool)


class GetDiagScript(BaseScript):
    name = "OS.Linux.get_diag"
    interface = IGetDict

    def execute_cli(self, **kwargs):
        r = {"motd": self.motd.strip(), "args": self.args}
        # cat /etc/motd
        r["cat-motd"] = self.cli("cat /etc/motd").strip()
        # pager
        self.cli("more /etc/services")
        # Nested scripts
        r["fqdn"] = self.scripts.get_fqdn()
        return r


@pytest.mark.parametrize(
    ("proto", "host", "port", "user", "password", "args", "xcls"),
    [
        # Plain call (ssh)
        ("ssh", SSHD_HOST, SSHD_PORT, TEST_USER, TEST_PW, {}, None),
        # Call with args (ssh)
        (
            "ssh",
            SSHD_HOST,
            SSHD_PORT,
            TEST_USER,
            TEST_PW,
            {"x": 1, "y": 2},
            None,
        ),
        # Connection refused
        ("ssh", SSHD_HOST, 1022, TEST_USER, TEST_PW, {}, CLIConnectionRefused),
        # Invalid user (ssh)
        (
            "ssh",
            SSHD_HOST,
            SSHD_PORT,
            BROKEN_USER,
            TEST_PW,
            {},
            CLIAuthFailed,
        ),
        # Invalid password (ssh)
        (
            "ssh",
            SSHD_HOST,
            SSHD_PORT,
            TEST_USER,
            BROKEN_PW,
            {},
            CLIAuthFailed,
        ),
        # Plain call (ssh)
        (
            "ssh",
            DROPBEAR_HOST,
            DROPBEAR_PORT,
            TEST_USER,
            TEST_PW,
            {},
            None,
        ),
        # Call with args (ssh)
        (
            "ssh",
            DROPBEAR_HOST,
            DROPBEAR_PORT,
            TEST_USER,
            TEST_PW,
            {"x": 1, "y": 2},
            None,
        ),
        # Connection refused
        ("ssh", DROPBEAR_HOST, 1022, TEST_USER, TEST_PW, {}, CLIConnectionRefused),
        # Invalid user (ssh)
        (
            "ssh",
            DROPBEAR_HOST,
            DROPBEAR_PORT,
            BROKEN_USER,
            TEST_PW,
            {},
            CLIAuthFailed,
        ),
        # Invalid password (ssh)
        (
            "ssh",
            DROPBEAR_HOST,
            DROPBEAR_PORT,
            TEST_USER,
            BROKEN_PW,
            {},
            CLIAuthFailed,
        ),
        # Plain call (telnet)
        (
            "telnet",
            TELNETD_HOST,
            TELNETD_PORT,
            TEST_USER,
            TEST_PW,
            {},
            None,
        ),
        # Call with args (telnet)
        (
            "telnet",
            TELNETD_HOST,
            TELNETD_PORT,
            TEST_USER,
            TEST_PW,
            {"x": 1, "y": 2},
            None,
        ),
        # Connection refused
        ("telnet", TELNETD_HOST, 1023, TEST_USER, TEST_PW, {}, CLIConnectionRefused),
        # Invalid user (telnet)
        (
            "telnet",
            TELNETD_HOST,
            TELNETD_PORT,
            BROKEN_USER,
            TEST_PW,
            {},
            CLIAuthFailed,
        ),
        # Invalid password (telnet)
        (
            "telnet",
            TELNETD_HOST,
            TELNETD_PORT,
            TEST_USER,
            BROKEN_PW,
            {},
            CLIAuthFailed,
        ),
    ],
)
def test_cli(proto, host, port, user, password, args, xcls):
    try:
        address = socket.gethostbyname(host)
    except socket.gaierror:
        pytest.fail("Cannot resolve host '{host}'")
    scr = GetDiagScript(
        service=ServiceStub(),
        credentials={
            "cli_protocol": proto,
            "address": address,
            "cli_port": port,
            "user": user,
            "password": password,
        },
        capabilities={},
        args=args,
        version={},
        timeout=60,
    )
    # Run script
    if xcls:
        with pytest.raises(xcls):
            scr.run()
        return
    result = scr.run()
    # Perform checks
    assert result
    print(f"<<<{result['motd']}>>>")
    print(f">>>{result['cat-motd']}<<<")
    assert result["motd"] == result["cat-motd"]
    assert result["args"] == args
    assert result["fqdn"]
