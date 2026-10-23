# ---------------------------------------------------------------------
# TPLink.EAP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "TPLink.EAP.get_version"
    interface = IGetVersion
    cache = True

    def execute_snmp(self):
        platform = self.snmp.get("1.3.6.1.4.1.11863.10.1.10.3.0", cached=True)
        version = self.snmp.get("1.3.6.1.4.1.11863.10.1.10.5.0", cached=True)
        return {"vendor": "TPLink", "version": version, "platform": platform}
