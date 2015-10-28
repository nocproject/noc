# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetInventory


class Script(BaseScript):
    name = "Supertel.K2X.get_inventory"
    interface = IGetInventory
    cache = True

    rx_description = re.compile(
        r"^System Description:\s+(?P<description>.+)$", re.MULTILINE)
    rx_hardware = re.compile(
        r"^HW version\s+(?P<hardware>\S+)$", re.MULTILINE)
    rx_serial = re.compile(
        r"^Serial number\s*:\s*(?P<serial>\S+)$", re.MULTILINE)
    rx_platform = re.compile(
        r"^System Object ID:\s+(?P<platform>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                platform = self.snmp.get("1.3.6.1.2.1.1.2.0", cached=True)
                platform = self.profile.platforms[platform.split('.')[8]]
                description = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.67108992",
                                         cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67108992",
                                       cached=True)
                return [{
                    "type": "CHASSIS",
                    "number": "1",
                    "builtin": False,
                    "vendor": "Supertel",
                    "part_no": [platform],
                    "description": description,
                    "revision": hardware,
                    "serial": serial
                }]
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        plat = self.cli("show system", cached=True)
        match = self.rx_platform.search(plat)
        platform = match.group("platform")
        platform = self.profile.platforms[platform.split('.')[8]]
        description = self.rx_description.search(plat)

        ver = self.cli("show version", cached=True)
        hardware = self.rx_hardware.search(ver)

        serial = self.cli("show system id", cached=True)
        serial = self.rx_serial.search(serial)

        return [{
                "type": "CHASSIS",
                "number": "1",
                "builtin": False,
                "vendor": "Supertel",
                "part_no": [platform],
                "description": description.group("description"),
                "revision": hardware.group("hardware"),
                "serial": serial.group("serial")
                }]
