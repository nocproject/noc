# ---------------------------------------------------------------------
# Eltex.LTP16N.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.LTP16N.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(
        r"^\s*([Tt][Yy][Pp][Ee]|Device\s+name):\s+(?P<platform>\S+)\s*\n"
        r"^\s*(Revision|Hardware\s+revision):\s+(?P<hardware>\S+)\s*\n"
        r"^\s*(SN|Serial\s+number):\s+(?P<serial>\S+)",
        re.MULTILINE,
    )

    rx_version = re.compile(
        r"Eltex (?P<platform>\S+): software version (?P<version>\S+\s+build\s+\d+)\s+.+"
    )

    def execute_snmp(self, **kwargs):
        oids = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0], cached=True)
        oids = oids.split(".")[8]
        oids = self.profile.get_platform(oids)

        v = self.snmp.get(oids["SW"])
        match = self.rx_version.search(v)
        platform = match.group("platform")
        version = match.group("version")
        hardware = self.snmp.get(oids["HW"])
        serial = self.snmp.get(oids["SN"])
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
