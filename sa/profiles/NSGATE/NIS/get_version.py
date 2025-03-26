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

    rx_platform = re.compile(
        r"Product\s+(?P<platform>\S+)\s+\S+\s*"
        r"Version (?P<version>\S+) \(\S+ \S+\)", re.MULTILINE
    )

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
        match = self.rx_platform.match(v)
        if not match:
            raise NotImplementedError()
        return {
            "vendor": "NSGATE",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
