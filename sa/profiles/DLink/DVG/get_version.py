# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DVG.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "DLink.DVG.get_version"
    implements = [IGetVersion]
    cache = True

    rx_platform = re.compile(
        r"^Software \[(==|\S+ ==) Ver\(+(?P<version>\S+)\s+\S+\s+\S+\)\s+PId\(+\S+\)\s+Drv\(+\S+\)\s+Hw\(+(?P<platform>\S+)+\) (== |== (?P<hardware>\S+))+\]$",
        re.MULTILINE)

    platforms_cli = {
        "??????": "DVG-2101S",
        "DSA": "DVG-2102S",
        "PNP1632-32": "DVG-4032S",
        "SA7S4": "DVG-5004S",
        "TSO": "DVG-7111S",
        }

    platforms_snmp = {
        "3.2.10": "DVG-2101S",
        "?.?.?": "DVG-2102S",
        "?.?.?": "DVG-4032S",
        "1.2.1": "DVG-5004S",
        "?.?.?": "DVG-7111S",
        }

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                platform = self.snmp.get("1.3.6.1.2.1.1.2.0", cached=True)
                platform = platform.split(', ')
                l = len(platform) - 1
                platform = (platform[l - 2] + '.' + platform[l - 1] +
                            '.' + platform[l])
                platform = self.platforms_snmp.get(platform.split(')')[0],
                                                   '????')
                return {
                    "vendor": "DLink",
                    "platform": platform,
                    "version": '1.02.38.x',
                    }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        plat = self.cli("GET STATUS HARDWARE", cached=True)
        match = self.rx_platform.search(plat)
        platform = self.platforms_cli.get(match.group("platform"), '????')
        r = {
            "vendor": "DLink",
            "platform": platform,
            "version": match.group("version"),
            }
        if match.group("hardware"):
            r["attributes"]["HW version"] = match.group("hardware")
        return r
