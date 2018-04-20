# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_vlans"
    interface = IGetVlans
=======
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_vlans"
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_vlan_line = re.compile(
        r"^(?P<vlan_id>\s{1,3}\d{1,4})\s+(?P<name>\S+)\s", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan_line.finditer(self.cli("show vlan")):
            vlanid = int(match.group("vlan_id"))
            if vlanid == 1:
                r += [{
                    "vlan_id": 1
                }]
            else:
                r += [{
                    "vlan_id": vlanid,
                    "name": match.group("name")
                }]
        return r
