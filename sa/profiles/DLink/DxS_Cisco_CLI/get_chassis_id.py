# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_chassis_id"
    interface = IGetChassisID
    rx_ver = re.compile(r"^Hardware is  VLAN, address is (?P<id>\S+)\s+",
                        re.IGNORECASE | re.MULTILINE)
    rx_mac_from = re.compile(r"^\s+Chassis\s+ID\s+:\s+(?P<mac_from>\S+)",
                             re.IGNORECASE | re.MULTILINE)

    def execute(self):
        match1 = self.re_search(
            self.rx_mac_from, self.cli("show lldp local-information global"))
        mac_from = match1.group("mac_from")
        match = self.re_search(self.rx_ver, self.cli("show interfaces vlan 1"))
        mac_to = match.group("id")
        return {
            "first_chassis_mac": mac_from,
            "last_chassis_mac": mac_to
        }
