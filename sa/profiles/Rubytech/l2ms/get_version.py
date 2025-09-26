# ---------------------------------------------------------------------
# Rubytech.l2ms.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
Test on:
- FGS-2824
- ES-2310C

> show


Model Name                   : ES-2310C
System Description           : 8 Fast Ethernet + 2 Gigabit L2 Managed Switch
Location                     : skatovka
Contact                      :
Device Name                  : ES-2310C
System Up Time               : 0 Days 0 Hours 22 Mins 51 Secs
Current Time                 : Wed Dec 21 01:10:15 2016
BIOS Version                 : v1.08
Firmware Version             : v2.32
Hardware-Mechanical Version  : v1.01-v1.01
Serial Number                : 031711040348
Host IP Address              : 10.64.160.250
Host MAC Address             : 00-40-c7-f6-bb-5b
Device Port                  : UART * 1  TP *8  Fiber * 2
RAM Size                     : 16 M
Flash Size                   : 2 M





"""

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Rubytech.l2ms.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Model Name\s+:\s(?P<platform>[^, ]+)\n"
        r".*BIOS Version\s+:\s(?P<biosversion>[^, ]+)\n"
        r".*Firmware Version\s+:\s(?P<version>[^, ]+)\n"
        r".*Hardware-Mechanical Version\s+:\s(?P<hwversion>[^, ]+)\n"
        r".*Serial Number\s+:\s(?P<sn>[^, ]+)\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute(self):
        ver = ""
        self.cli("system", cached=True)

        ver = self.cli("show", cached=True)
        match = self.re_search(self.rx_ver, ver)
        return {
            "vendor": "Rubytech",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "HW version": match.group("hwversion"),
                "Serial Number": match.group("sn"),
                "Boot PROM": match.group("biosversion"),
            },
        }
