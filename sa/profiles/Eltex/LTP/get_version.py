# ---------------------------------------------------------------------
# Eltex.LTP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.LTP.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(
        r"^\s*TYPE:\s+(?P<platform>\S+)\s*\n"
        r"^\s*HW_revision:\s+(?P<hardware>\S+)\s*\n"
        r"^\s*SN:\s+(?P<serial>\S+)",
        re.MULTILINE,
    )

    rx_version = re.compile(
        r"^Eltex (?P<platform>\S+) software version (?P<version>\S+\s+build\s+\d+)\s+"
    )

    def execute_snmp(self, **kwargs):
        v = self.snmp.get("1.3.6.1.4.1.35265.1.22.1.1.6.0")
        match = self.rx_version.search(v)
        platform = match.group("platform")
        version = match.group("version")
        hardware = self.snmp.get("1.3.6.1.4.1.35265.1.22.1.1.8.0")
        serial = self.snmp.get("1.3.6.1.4.1.35265.1.22.1.18.4.0")
        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hardware, "Serial Number": serial},
        }

    def execute_cli(self, **kwargs):
        try:
            plat = self.cli("show system environment", cached=True)
        except self.CLISyntaxError:
            raise NotImplementedError
        match = self.rx_platform.search(plat)
        platform = match.group("platform")
        hardware = match.group("hardware")
        serial = match.group("serial")

        ver = self.cli("show version", cached=True)
        match = self.rx_version.search(ver)
        if platform:
            platform = match.group("platform")
        version = match.group("version")

        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hardware, "Serial Number": serial},
        }
