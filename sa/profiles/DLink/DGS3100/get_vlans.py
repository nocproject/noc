# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "DLink.DGS3100.get_vlans"
    interface = IGetVlans
    rx_vlan = re.compile(
        r"^\s*VID\s+:\s+(?P<vlanid>\S+).+VLAN Name\s+:\s+(?P<vlanname>\S+)$",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r += [{
                "vlan_id": int(match.group('vlanid')),
                "name": match.group('vlanname')
            }]
        return r
