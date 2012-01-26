# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_vlans
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
    name = "DLink.DxS.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(r"^VID\s+:\s+(?P<vlanid>\S+).+VLAN Name\s+:\s+(?P<vlanname>\S+)$", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r.append({
                "vlan_id": int(match.group('vlanid')),
                "name": match.group('vlanname')
            })
        return r
