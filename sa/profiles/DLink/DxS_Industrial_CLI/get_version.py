# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^\s*(?P<unit>\d+)\s+(?P<platform>D\S+)\s+H/W:(?P<hardware>\S+)\s*\n"
        r"^\s+Bootloader:(?P<bootprom>\S+)\s*\n"
        r"^\s+Runtime:(?P<version>\S+)\s*\n",
        re.MULTILINE)

    def execute_cli(self):
        c = self.cli("show version", cached=True)
        match = self.rx_ver.search(c)
        return {
            "vendor": "DLink",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware")
            }
        }
