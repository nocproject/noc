# ----------------------------------------------------------------------
# Vertiv.PDU.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Vertiv.PDU.get_version"
    cache = True
    interface = IGetVersion

    def execute_snmp(self, **kwargs):
        # productPlatform - .1.3.6.1.4.1.21239.5.2.1.11.0
        platform = self.snmp.get("1.3.6.1.4.1.21239.5.2.1.1.0")
        firmware = self.snmp.get("1.3.6.1.4.1.21239.5.2.1.2.0")
        if not platform:
            # Use SysName for old version
            platform = self.snmp.get(mib["SNMPv2-MIB::sysName", 0])
        if not platform:
            raise self.NotSupportedError
        return {"vendor": "Vertiv", "platform": platform, "version": firmware}
