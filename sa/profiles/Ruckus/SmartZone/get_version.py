# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.SmartZone.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Ruckus.SmartZone.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                platform = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                serial = self.snmp.get("1.3.6.1.4.1.25053.1.4.1.1.1.15.13.0", cached=True)
                return {
                    "vendor": "Ruckus",
                    "version": "3.4.1.0.38",  # no oid
                    "platform": platform,
                    "attributes": {"Serial Number": serial},
                }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
