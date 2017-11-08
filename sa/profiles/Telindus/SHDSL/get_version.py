# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Telindus.SHDSL.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Telindus.SHDSL.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                c = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                v = c.split("$")
                pr = v[1].split()
                platform = pr[1].strip()
                vr = v[2].split()
                for ver in vr:
                    if ver.startswith("T"):
                        version = ver
                return {
                    "vendor": "Telindus",
                    "version": version,
                    "platform": platform
                }
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        raise Exception("Not implemented")
