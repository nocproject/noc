# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.7324RU.get_config
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alcatel.7324RU.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"Model\s*:\s*(?P<platform>.+?)\s*$",
                        re.MULTILINE | re.DOTALL)
    rx_ver = re.compile(r".+?version\s*:\s*(?P<version>.+?)\s+\|.*$",
                        re.MULTILINE | re.DOTALL)
    rx_boot_ver = re.compile(r"Bootbase version: (?P<bootprom>\S+)")
    rx_hw_ver = re.compile(r"Hardware version: (?P<hw_version>\S+)")
    rx_serial = re.compile(r"Serial number: (?P<serial>\S+)")

    def execute(self):
        v = self.cli("sys info show", cached=True)
        match_sys = self.rx_sys.search(v)
        match_ver = self.rx_ver.search(v)
        r = {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version"),
            "attributes": {}
        }
        match = self.rx_boot_ver.search(v)
        if match:
            r["attributes"]["Boot PROM"] = match.group("bootprom")
        match = self.rx_hw_ver.search(v)
        if match:
            r["attributes"]["HW version"] = match.group("hw_version")
        match = self.rx_serial.search(v)
        if match:
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
