# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QFC_PBIC_Lite.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Qtech.QFC_PBIC_Lite.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                platform = self.snmp.get("1.3.6.1.4.1.27514.101.1.101").strip()
                version = self.snmp.get("1.3.6.1.4.1.27514.101.1.1")
                result = {
                    "vendor": "Qtech",
                    "version": version,
                    "platform": platform
                }
                return result
            except self.snmp.TimeOutError:
                pass
