# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES24xx.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.MES24xx.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(
        r"^Hardware Version\s+: (?P<hardware>\S+)\s*\n"
        r"^Software Version\s+: (?P<version>\S+)\s*\n"
        r"^Firmware Version\s+: (?P<bootprom>\S+)\s*\n"
        r"(^\s*\n)?"
        r"^Hardware Serial Number\s+: (?P<serial>\S+)\s*\n"
        r"^Software Serial Number\s+:.*\n"
        r"^System Contact\s+:.*\n"
        r"^System Name\s+:.*\n"
        r"^System Location\s+:.*\n"
        r"^System Description\s+: (?P<platform>\S+) .+\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        ver = self.cli("show system information", cached=True)
        match = self.rx_version.search(ver)
        r = {
            "vendor": "Eltex",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Serial Number": match.group("serial"),
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
            },
        }
        return r
