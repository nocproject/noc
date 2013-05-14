# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_chassis_id"
    cache = True
    rx_ver = re.compile(r"^Hardware is  VLAN, address is (?P<id>\S+)\s+",
                        re.IGNORECASE | re.MULTILINE)
    rx_mac_from = re.compile(r"^\s+Chassis\s+ID\s+:\s+(?P<mac_from>\S+)",
                             re.IGNORECASE | re.MULTILINE)
    implements = [IGetChassisID]

    def execute(self):
        match1 = self.re_search(self.rx_mac_from, self.cli("show lldp local-information global", cached=True))
        mac_from = match1.group("mac_from")
        match = self.re_search(self.rx_ver, self.cli("show interfaces vlan 1",
                               cached=True))
        mac_to = match.group("id")
        return {
            "first_chassis_mac": mac_from,
            "last_chassis_mac": mac_to
        }
