# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.7302.get_version
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Alcatel.7302.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"actual-type\s*?:\s*(?P<platform>.+?)\s*$", re.MULTILINE)
    rx_slots = re.compile(r"slot count\s*:\s*(?P<slot_count>\d+)")
    rx_ver = re.compile(r".+?\/*(?P<version>[A-Za-z0-9.]+?)\s+\S+\s+active.*$", re.MULTILINE)

    port_map = {7: "7330 iSAM", 19: "7302 iSAM"}  # 16, 2  # 8, 2  # 24, 2

    def execute_cli(self, **kwargs):
        self.cli("environment inhibit-alarms mode batch", ignore_errors=True)
        v = self.cli("show equipment slot")
        slots = self.rx_slots.search(v)
        v = self.cli("show software-mngt oswp")
        match_ver = self.rx_ver.search(v)
        return {
            "vendor": "Alcatel",
            "platform": self.port_map[int(slots.group("slot_count"))],
            "version": match_ver.group("version"),
        }
