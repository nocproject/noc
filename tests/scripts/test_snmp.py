# ----------------------------------------------------------------------
# SNMP testing
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
from noc.core.snmp.version import SNMP_v2c
from noc.sa.interfaces.igetdict import IGetDict
from noc.core.script.snmp.base import SNMP
from noc.core.mib import mib
from noc.config import config


SNMP_HOST = config.tests.snmpd_host
SNMP_PORT = config.tests.snmpd_port
SNMP_COMMUNITY = "public"


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

    def execute_snmp(self, **kwargs):
        r = {}
        # Get location
        r["location"] = self.snmp.get(mib["SNMPv2-MIB::sysLocation", 0])
        # Getnext
        r["if_getnext"] = self.snmp.getnext(mib["IF-MIB::ifName"], bulk=False)
        # getbulk
        r["if_getbulk"] = self.snmp.getnext(mib["IF-MIB::ifName"], bulk=True)
        return r


@pytest.mark.parametrize(
    ("host", "version", "community", "xcls"),
    [
        (SNMP_HOST, SNMP_v2c, SNMP_COMMUNITY, None),
        (SNMP_HOST, SNMP_v2c, SNMP_COMMUNITY + "X", SNMP.TimeOutError),
    ],
)
def test_snmp(host, version, community, xcls):
    try:
        address = socket.gethostbyname(host)
    except socket.gaierror:
        pytest.fail(f"Cannot resolve host '{host}'")
    scr = GetDiagScript(
        service=ServiceStub(),
        credentials={"access_preference": "S", "address": address, "snmp_ro": community},
        capabilities={},
        args={},
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
    assert result["location"]
    assert result["if_getnext"]
    assert result["if_getbulk"]
    assert result["if_getnext"] == result["if_getbulk"]
