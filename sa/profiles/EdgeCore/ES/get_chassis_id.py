# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "EdgeCore.ES.get_chassis_id"
    cache = True
    implements = [IGetChassisID]
    rx_mac_4626 = re.compile(r"\d+\s+(?P<id>\S+).*?System\s+CPU",
        re.IGNORECASE | re.MULTILINE)
    rx_mac_3528mv2 = re.compile(
        r"\sMAC\sAddress\s+\(Unit\s\d\)\s+:\s+(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
    rx_mac = re.compile(r"MAC Address[^:]*?:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    ##
    ## ES4626
    ##
    @NOCScript.match(platform__contains="4626")
    def execute_4626(self):
        v = self.cli("show mac-address-table static")
        match = self.re_search(self.rx_mac_4626, v)
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }

    ##
    ## Other
    ##
    @NOCScript.match()
    def execute_other(self):
        if self.match_version(platform__contains="3528MV2"):
            v = self.cli("show system\n")               # ES-3538MV2
            match = self.rx_mac_3528mv2.search(v)
        else:
            v = self.cli("show system")
            match = self.re_search(self.rx_mac, v)
        first_mac = match.group("id")
        v = self.cli("show int statu")
        for l in v.splitlines():
            match = self.rx_mac.search(l)
            if match:
                if match.group("id") != first_mac:
                    last_mac = match.group("id")
        if not last_mac:
            last_mac = first_mac
        return {
            "first_chassis_mac": first_mac,
            "last_chassis_mac": last_mac
        }
