# ---------------------------------------------------------------------
# ElectronR.KO01M.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "ElectronR.KO01M.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

    def execute_snmp(self):
        platform = self.snmp.get("1.3.6.1.2.1.1.1.0").split()[1]
        sn = self.snmp.get("1.3.6.1.4.1.35419.1.1.1.0")
        version = self.snmp.get("1.3.6.1.4.1.35419.1.1.2.0")
        return {
            "vendor": "Electron",
            "version": version,
            "platform": platform.strip(),
            "attributes": {"Serial Number": sn},
        }
