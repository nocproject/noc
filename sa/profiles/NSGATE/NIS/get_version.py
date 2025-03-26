# ---------------------------------------------------------------------
# Host.SNMP.get_version
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
    name = "Host.SNMP.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(r"HPE OfficeConnect Switch\s+(?P<platform>.+)")

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
        return {"vendor": "NSGATE", "platform": v, "version": "", "sysobjectid": v}
