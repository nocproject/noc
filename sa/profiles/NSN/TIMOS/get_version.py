# ----------------------------------------------------------------------
# NSN.TIMOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "NSN.TIMOS.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"System Type\s+:\s+(?P<platform>.+?)$", re.MULTILINE | re.DOTALL)
    rx_ver = re.compile(r"System Version\s+:\s+(?P<version>.+?)$", re.MULTILINE | re.DOTALL)
    rx_ver_snmp = re.compile(r"TiMOS-(?P<version>.+?)\s", re.MULTILINE | re.DOTALL)

    CHASSIS_TYPES = {
        2: "7750 SR-12",
        4: "7750 SR-4",
        5: "7750 SR-1",
        6: "7750 SR-7",
        14: "7750 SR-12e",
        30: "7750 SR-1e",
        31: "7750 SR-2e",
        33: "7750 SR-3e",
        37: "7750 SR-14s",
        39: "7750 SR-1",
        44: "7750 SR-7s",
        46: "7750 SR-1s",
        47: "7750 SR-2s",
    }

    def execute_snmp(self):
        try:
            v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        except (self.snmp.TimeOutError, self.snmp.SNMPError):
            raise NotImplementedError()
        if "TiMOS" in v:
            match = self.re_search(self.rx_ver_snmp, v)
            version = match.group("version")
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.2.1.3.1.4", cached=True):
            platform = self.CHASSIS_TYPES[v]
        return {
            "vendor": "NSN",
            "platform": platform,
            "version": version,
        }

    def execute_cli(self):
        v = self.cli("show system information")
        match_sys = self.re_search(self.rx_sys, v)
        match_ver = self.re_search(self.rx_ver, v)
        return {
            "vendor": "NSN",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version"),
        }
