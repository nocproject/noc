# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# GWD.GFA.get_version
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
    name = "GWD.GFA.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(r"^ProductOS Version (?P<version>\S+)", re.MULTILINE)
    rx_hardware = re.compile(
        r"^CHASSIS : (?P<platform>\S+)\s+(?P<hardware>\S+)\s+\d{4}\-\d\d\-\d\d\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_version.search(v)
        version = match.group("version")
        match = self.rx_hardware.search(v)

        return {
            "vendor": "GWD",
            "platform": match.group("platform"),
            "version": version,
            "attributes": {
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial"),
            },
        }
