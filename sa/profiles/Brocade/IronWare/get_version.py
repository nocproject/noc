# ---------------------------------------------------------------------
# Brocade.IronWare.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Brocade.IronWare.get_version"
    interface = IGetVersion
    cache = True

    rx_sw_ver = re.compile(r"SW:\sVersion\s(?P<version>\S+)", re.MULTILINE | re.DOTALL)
    rx_hw_ver = re.compile(r"HW:\s+(?P<version>\S+\s+\S+\s+\S+),", re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(
        r"ProCurve\s+\S+\s+\S+\s(?P<platform>\S+)\,\s+\S+\s+Version\s+(?P<version>\S+).+$"
    )

    def execute_snmp(self):
        v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
        match = self.self.rx_snmp_ver.search(v)
        return {
            "vendor": "Brocade",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match1 = self.rx_sw_ver.search(v)
        match2 = self.rx_hw_ver.search(v)
        return {
            "vendor": "Brocade",
            "platform": match2.group("version"),
            "version": match1.group("version"),
        }
