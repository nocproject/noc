# ---------------------------------------------------------------------
# Eltex.ESR.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.ESR.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"System type:\s+Eltex\s+(?P<platform>\S+)\s+.+\n"
        r"System name:\s+\S+\s*\n"
        r"Software version:\s+(?P<version>.+) \(date .+\n"
        r"Hardware version:\s+(?P<hardware>\S+)\s*\n"
        r"System uptime:.+\n"
        r"System MAC address:\s+\S+\s*\n"
        r"System serial number:\s+(?P<serial>\S+)\s*\n"
    )

    rx_ver_snmp = re.compile(r"^(?P<version>.*) \(date")

    def execute_cli(self):
        c = self.scripts.get_system()
        match = self.rx_ver.search(c)
        return {
            "vendor": "Eltex",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial"),
            },
        }

    def execute_snmp(self):
        hw = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.680000")
        version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.680000")
        match = self.rx_ver_snmp.search(version)
        sn = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.680000")
        platform = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.13.680000")
        return {
            "vendor": "Eltex",
            "platform": "ESR-%s" % platform,
            "version": match.group("version"),
            "attributes": {
                "HW version": hw,
                "Serial Number": sn,
            },
        }
