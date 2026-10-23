# ---------------------------------------------------------------------
# NSGATE.NIS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "NSGATE.NIS.get_version"
    interface = IGetVersion
    cache = True

    rx_industrial_platform = re.compile(
        r"Product\s+(?P<platform>\S+)\s+\S+\s*Version (?P<version>\S+) \(\S+ \S+\)",
        re.MULTILINE,
    )
    rx_platform = re.compile(r"^(?P<platform>NIS-\S+),")
    rx_version = re.compile(r"Version\s+(?P<version>\S+)")

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
        match_p = self.rx_platform.search(v)
        if not match_p:
            raise NotImplementedError()
        match_v = self.rx_version.search(v)
        if match_v:
            version = match_v.group("version")
        else:
            version = ""
        return {
            "vendor": "NSGATE",
            "platform": match_p.group("platform"),
            "version": version,
        }
