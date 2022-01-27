# ---------------------------------------------------------------------
# Iskratel.MSAN.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Iskratel.MSAN.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(r"(Machine Model|Board Type)\.+\s+(?P<platform>.+)\n")
    rx_serial = re.compile(r"(Board Serial Number|Serial Number)\.+ (?P<serial>\S+)\n")

    rx_ver = re.compile(r"(Steer|Appl\.|Package)\s*Version\.+\s*(?P<version>\S+)")

    def execute_snmp(self, **kwargs):
        version = self.snmp.get("1.3.6.1.4.1.1332.1.1.5.1.3.1.0")
        return {
            "vendor": "Iskratel",
            "platform": "Iskratel SGR",
            "version": version,
            # "attributes": {"Serial Number": serial},
        }

    def execute_cli(self):
        v = self.cli("show hardware", cached=True)
        match = self.rx_platform.search(v)
        if match:
            platform = match.group("platform")
        else:
            raise NotImplementedError
        match = self.rx_serial.search(v)
        if match:
            serial = match.group("serial")
        # 1.3.6.1.4.1.1332.1.1.5.1.3.11.1.3.1
        c = self.cli("show version")
        match = self.rx_ver.search(c)
        version = match.group("version")
        return {
            "vendor": "Iskratel",
            "platform": platform,
            "version": version,
            "attributes": {"Serial Number": serial},
        }
