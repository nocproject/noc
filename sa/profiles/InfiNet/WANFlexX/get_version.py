# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_version
# Izya12@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"PN:(?P<platform>.+)\/")
    rx_ver = re.compile(r"WANFleX\s+(?P<version>\S+)")
    rx_sn = re.compile(r"SN:(?P<sn>\d+)")
    rx_hardware = re.compile(r"PN:.+\/(?P<hardware>\S+)")

    def execute(self):
        v = self.cli("system version", cached=True)
        match = self.re_search(self.rx_ver, v)
        version = match.group("version")
        match = self.re_search(self.rx_platform, v)
        platform = match.group("platform")
        match = self.re_search(self.rx_sn, v)
        sn = match.group("sn")
        match = self.re_search(self.rx_hardware, v)
        hardware = match.group("hardware")
        r = {
            "vendor": "InfiNet",
            "platform": platform,
            "version": version,
            "attributes": {
                "HW version": hardware,
                "Serial Number": sn
            }
        }
        return r
