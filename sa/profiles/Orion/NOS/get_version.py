# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Orion.NOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Orion.NOS.get_version"
    cache = True
    interface = IGetVersion

    def execute_cli(self):
        v = self.profile.get_version(self)
        return {
            "vendor": "Orion",
            "platform": v["platform"],
            "version": v["version"],
            "attributes": {
                "Serial Number": v["serial"],
                "Boot PROM": v["bootprom"],
                "HW version": v["hardware"],
            },
        }
