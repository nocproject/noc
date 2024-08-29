# ----------------------------------------------------------------------
# CLI testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
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


SSHD_HOST = "sshd"
DROPBEAR_HOST = "dropbear"
TELNETD_HOST = "telnetd"
TEST_USER = "test"
TEST_PW = "pw1234567890"


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
    "proto,host,port,user,password,args,xcls",
    [
        # Plain call (ssh)
        ("ssh", SSHD_HOST, 22, TEST_USER, TEST_PW, {}, None),
        # Call with args (ssh)
        ("ssh", SSHD_HOST, 22, TEST_USER, TEST_PW, {"x": 1, "y": 2}, None),
        # Connection refused
        ("ssh", SSHD_HOST, 1022, TEST_USER, TEST_PW, {}, CLIConnectionRefused),
        # Invalid user (ssh)
        ("ssh", SSHD_HOST, 22, TEST_USER + "X", TEST_PW, {}, CLIAuthFailed),
        # Invalid password (ssh)
        ("ssh", SSHD_HOST, 22, TEST_USER, TEST_PW + "X", {}, CLIAuthFailed),
        # Plain call (ssh)
        ("ssh", DROPBEAR_HOST, 22, TEST_USER, TEST_PW, {}, None),
        # Call with args (ssh)
        ("ssh", DROPBEAR_HOST, 22, TEST_USER, TEST_PW, {"x": 1, "y": 2}, None),
        # Connection refused
        ("ssh", DROPBEAR_HOST, 1022, TEST_USER, TEST_PW, {}, CLIConnectionRefused),
        # Invalid user (ssh)
        ("ssh", DROPBEAR_HOST, 22, TEST_USER + "X", TEST_PW, {}, CLIAuthFailed),
        # Invalid password (ssh)
        ("ssh", DROPBEAR_HOST, 22, TEST_USER, TEST_PW + "X", {}, CLIAuthFailed),
        # Plain call (telnet)
        ("telnet", TELNETD_HOST, 23, TEST_USER, TEST_PW, {}, None),
        # Call with args (telnet)
        ("telnet", TELNETD_HOST, 23, TEST_USER, TEST_PW, {"x": 1, "y": 2}, None),
        # Connection refused
        ("telnet", TELNETD_HOST, 1023, TEST_USER, TEST_PW, {}, CLIConnectionRefused),
        # Invalid user (telnet)
        ("telnet", TELNETD_HOST, 23, TEST_USER + "X", TEST_PW, {}, CLIAuthFailed),
        # Invalid password (telnet)
        ("telnet", TELNETD_HOST, 23, TEST_USER, TEST_PW + "X", {}, CLIAuthFailed),
    ],
)
def test_cli(proto, host, port, user, password, args, xcls):
    try:
        address = socket.gethostbyname(host)
    except socket.gaierror:
        pytest.fail("Cannot resolve host '%s'" % host)
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
    assert result["motd"] == result["cat-motd"]
    assert result["args"] == args
    assert result["fqdn"]
