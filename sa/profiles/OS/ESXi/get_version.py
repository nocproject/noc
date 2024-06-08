# ---------------------------------------------------------------------
# OS.ESXi.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib
import re


class Script(BaseScript):
    name = "OS.ESXi.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(r"(?P<version>\S+)\s+(?P<platform>\S+)")
    rx_ver_snmp = re.compile(r"VMware (?P<platform>\S+)\s+(?P<version>.*) V")

    def execute_cli(self):
        match = self.re_search(self.rx_ver, self.cli("uname -m -r"))
        return {
            "vendor": "VmWare",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }

    def execute_snmp(self, **kwargs):
        platform = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        match = self.re_search(self.rx_ver_snmp, platform)
        return {
            "vendor": "VmWare",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
