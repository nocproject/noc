# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Telecom.FXS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Telecom.FXS.get_version"
    interface = IGetVersion
    cache = True
    always_prefer = "S"

    def execute_snmp(self, **kwargs):
        # mgCommonConfigPOTS
        platform = self.snmp.get("1.3.6.1.4.1.40248.4.1.87")
        # mgCommonConfigSoftwareVersion
        version = self.snmp.get("1.3.6.1.4.1.40248.4.1.85")
        # mgCommonConfigFactoryType
        vendor = self.snmp.get("1.3.6.1.4.1.40248.4.1.88")
        return {
            "vendor": vendor.strip(),
            "platform": platform.strip(),
            "version": version.strip(),
            "attributes": {},
        }
