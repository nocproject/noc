# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2500.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Qtech.QSW2500.get_version"
    interface = IGetVersion
    cache = True

    def execute_cli(self):
        ver = self.cli("show version", cached=True)
        match = self.profile.rx_ver.search(ver)
        return {
            "vendor": "Qtech",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial"),
            },
        }
