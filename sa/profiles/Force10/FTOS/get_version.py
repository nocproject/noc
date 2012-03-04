# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
##
## A list of known F10 chasiss type from FORCE10-TC
##
F10_CHASSIS = {
    1: "E1200",    # Force10 E1200 16-slot switch/router
    2: "E600",     # Force10 E600 9-slot switch/router
    3: "E300",     # Force10 E300 8-slot switch/router
    4: "E150",     # Force10 E150 8-slot switch/router
    5: "E600i",    # Force10 E600i 9-slot switch/router
    6: "C150",     # Force10 C150 6-slot switch/router
    7: "C300",     # Force10 C300 10-slot switch/router
    8: "E1200i",   # Force10 E1200i 16-slot switch/router
    9: "S2410cp",  # Force10 S2410 10GbE switch
    10: "S2410p",  # Force10 S2410 10GbE switch
    11: "S50",     # Force10 S50 access switch
    12: "S50E",    # Force10 S50e access switch
    13: "S50V",    # Force10 S50v access switch
    14: "S50N",    # Force10 S50nac access switch
    15: "S50N",    # Force10 S50ndc access switch
    16: "S25P",    # Force10 S25pdc access switch
    17: "S25P",    # Force10 S25pac access switch
    18: "S25V",    # Force10 S25v access switch
    19: "S25N",    # Force10 S25n access switch
}


class Script(NOCScript):
    name = "Force10.FTOS.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(r"Force10 Application Software Version: (?P<version>\S+).*(?:System|Chassis) Type: (?P<platform>\S+)", re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(
        r"Force10 Application Software Version:\s*(?P<version>\S+)",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get version from sysDescr.0
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                match = self.re_search(self.rx_snmp_ver, v)
                version = match.group("version")
                # Get platform from F10-CHASSIS-MIB::chType
                v = self.snmp.get("1.3.6.1.4.1.6027.3.1.1.1.1.0")
                # F10-CHASSIS-MIB seems to be unsupported on C-series
                if v == "":
                    raise self.snmp.TimeOutError  # Fallback to CLI
                platform = F10_CHASSIS[int(v)]
                return {
                    "vendor": "Force10",
                    "platform": platform,
                    "version": version,
                }
            except self.snmp.TimeOutError:
                pass

        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Force10",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
