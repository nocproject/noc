# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QOS.get_version
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
    name = "Qtech.QOS.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^Product Name: (?P<platform>\S+)\s*\n"
        r"^Hardware Version: (?P<hardware>\S+)\s*\n"
        r"^Bootstrap Version: (?P<bootprom>\S+)\s*\n"
        r"^Software Version: QOS_(?P<version>\S+)\s*\n"
        r"^PCB Version: .+\n"
        r"^FPGA Version: .+\n"
        r"^CPLD Version: .+\n"
        r"^QOS Version: .+\n"
        r"^BOM Version: .+\n"
        r"^Compiled .+\n"
        r"^\s*\n"
        r"^System MacAddress: (?P<mac>\S+)\s*\n"
        r"^Serial number: (?P<serial>\S+)\s*\n",
        re.MULTILINE
    )

    def execute(self):
        ver = self.cli("show version", cached=True)
        match = self.rx_ver.search(ver)
        return {
            "vendor": "Qtech",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial")
            }
        }
