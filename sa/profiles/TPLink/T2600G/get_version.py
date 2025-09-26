# ---------------------------------------------------------------------
# TPLink.T2600G.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

rx_platform = re.compile(r"\s+Hardware Version\s+- (?P<platform>.+?)\n")
rx_version = re.compile(r"\s+Software Version\s+- (?P<version>.+?)\n")


class Script(BaseScript):
    name = "TPLink.T2600G.get_version"
    interface = IGetVersion
    cache = True

    def execute_snmp(self, **kwargs):
        v = self.snmp.get("1.3.6.1.4.1.11863.6.1.1.5.0")
        platform, version = v.split()
        version = self.snmp.get("1.3.6.1.4.1.11863.6.1.1.6.0")
        serial = self.snmp.get("1.3.6.1.4.1.11863.6.1.1.8.0")
        return {
            "vendor": "TPLink",
            "platform": platform,
            "version": version,
            "attributes": {"Serial Number": serial},
        }

    def execute_cli(self):
        ver = self.cli("show system-info", cached=True)
        match = rx_platform.search(ver)
        platform = match.group("platform")
        match = rx_version.search(ver)
        version = match.group("version")

        return {"vendor": "TPLink", "platform": platform, "version": version}
