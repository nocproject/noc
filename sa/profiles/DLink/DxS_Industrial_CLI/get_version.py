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
        re.MULTILINE,
    )
    rx_serial = re.compile(r"^\s*(?P<unit>\d+)\s+(?P<serial>\S+)\s+ok\s+\S+\s*\n", re.MULTILINE)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        r = {
            "vendor": "DLink",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
            },
        }
        v = self.cli("show unit %s | include ok" % match.group("unit"), cached=True)
        match = self.rx_serial.search(v)
        if match:
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
