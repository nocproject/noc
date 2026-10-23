# ---------------------------------------------------------------------
# Ttronics.KUB.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Ttronics.KUB.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

    def execute_snmp(self):
        o = self.snmp.get("1.3.6.1.2.1.1.1.0")
        platform, version, _ = o.split(None, 2)
        return {"vendor": "Ttronics", "version": version, "platform": platform}
