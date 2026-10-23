# ---------------------------------------------------------------------
# VyOS.VyOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "VyOS.VyOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"^Version:\s+VyOS (?P<version>\d+\S+)", re.MULTILINE)
    rx_platform = re.compile(r"^Architecture:\s+(?P<platform>\S+)", re.MULTILINE)
    rx_snmp_ver = re.compile(r"^VyOS\s+(?P<version>\d+\S+)$")

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
        match = self.rx_snmp_ver.search(v)
        version = match.group("version")
        # Temporary hardcode `platform`
        return {"vendor": "VyOS", "platform": "x86_64", "version": version}

    def execute_cli(self):
        v = self.cli("show version")
        match = self.rx_ver.search(v)
        version = match.group("version")
        match = self.rx_platform.search(v)
        platform = match.group("platform")
        return {"vendor": "VyOS", "platform": platform, "version": version}
