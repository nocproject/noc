# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^(?P<platform>\S+) Ethernet Managed Switch\n"
        r"(^eNOS software, Compiled on .*\n)?"
        r"(^Copyright .*\n)?"
        r"(^All rights reserved\n)?"
        r"(^CPU Mac \S+\s*\n)?"
        r"(^Vlan MAC \S+\s*\n)?"
        r"^Soft[Ww]are Version (?P<version>\S+)\s*\n"
        r"^BootRom Version (?P<bootprom>\S+).*\n"
        r"^Hard[Ww]are Version (?P<hardware>\S+)*\n"
        r"^CPLD Version.*\n"
        r"^Serial No.: (?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        vendor = "NAG"
        return {
            "vendor": vendor,
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial"),
            },
        }
