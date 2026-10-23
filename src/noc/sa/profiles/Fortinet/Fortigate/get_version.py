# ---------------------------------------------------------------------
# Fortinet.Fortigate.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Fortinet.Fortigate.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Version:\s+(?P<platform>\S+)+\ (?P<version>\S+)", re.MULTILINE | re.DOTALL
    )
    rx_snmp_ver = re.compile(r"(?P<platform>\S+)+\ (?P<version>\S+)")

    def execute_snmp(self):
        try:
            serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1", cached=True)
            v = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1", cached=True)
            match = self.re_search(self.rx_snmp_ver, v)
            return {
                "vendor": "Fortinet",
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {"Serial Number": serial},
            }
        except self.snmp.TimeOutError:
            pass

    def execute_cli(self):
        v = self.cli("get system status")
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Fortinet",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
