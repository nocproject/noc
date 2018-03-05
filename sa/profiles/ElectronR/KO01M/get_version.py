# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ElectronR.KO01M.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                platform = self.snmp.get("1.3.6.1.2.1.1.1.0").strip().replace(" ", ".")
                sn = self.snmp.get("1.3.6.1.4.1.35419.1.1.1.0")
                version = self.snmp.get("1.3.6.1.4.1.35419.1.1.2.0")
                result = {
                    "vendor": "ElectronR",
                    "version": version,
                    "platform": platform,
                    "attributes": {
                        "Serial Number": sn}
                }
                return result
            except self.snmp.TimeOutError:
                pass
