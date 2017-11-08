# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.FlexGain.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Nateks.FlexGain.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Nateks\s*\n"
        r"System Description:(?P<platform>.+)\n"
        r"Hardware Version:(?P<hardware>\S+)\s*\n"
        r"Firmware Version:(?P<bootprom>\S+)\s*\n"
        r"Software Version:(?P<software>\S+)", re.MULTILINE)

    def execute(self):
        match = self.rx_ver.search(self.cli("show version"))
        return {
            "vendor": "Nateks",
            "platform": match.group("platform").strip(),
            "version": match.group("software"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
            }
        }
