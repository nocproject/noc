# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW8200.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Qtech.QSW8200.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"Product Name: (?P<platform>.*)\s*\n"
        r"(Product Version:.*\n)?"
        r"Hardware Version:(?P<hardware>.*)\n"
        r"Software Version: (?P<version>\S+)\(.+\)\s*\n"
        r"Q?OS Version:.*\n"
        r"REAP Version:.*\n"
        r"Bootrom Version:(?P<bootprom>.*)\n"
        r"\s*\n"
        r"System MAC Address:.*\n"
        r"Serial number:(?P<serial>.*)\n",
        re.MULTILINE
    )

    def execute(self):
        ver = self.cli("show version", cached=True)
        match = self.rx_ver.search(ver)
        platform = match.group("platform")
        version = match.group("version")
        bootprom = match.group("bootprom")
        hardware = match.group("hardware")
        serial = match.group("serial")
        r = {
            "vendor": "Qtech",
            "platform": platform,
            "version": version,
            "attributes": {}
        }
        if serial and serial.strip():
            r["attributes"]["Serial Number"] = serial.strip()
        if bootprom and bootprom.strip():
            r["attributes"]["Boot PROM"] = bootprom.strip()
        if hardware and hardware.strip():
            r["attributes"]["HW version"] = hardware.strip()
        return r
