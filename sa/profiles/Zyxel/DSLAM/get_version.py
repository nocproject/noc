# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.DSLAM.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Zyxel.DSLAM.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^\s*Model: \S+ / (?P<platform>\S+)\s*\n"
        r"^\s*ZyNOS version: (?P<version>\S+) \| \S+\s*\n"
        r".+?\n"
        r"^\s*Bootbase version: (?P<bootprom>\S+) \| \S+\s*\n"
        r".+?\n"
        r"^\s*Hardware version: (?P<hardware>\S+)\s*\n"
        r"^\s*Serial number: (?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        match = self.rx_ver.search(self.cli("sys info show"))
        return {
            "vendor": "ZyXEL",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial")
            }
        }
