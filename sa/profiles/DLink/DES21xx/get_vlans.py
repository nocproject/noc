# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.get_vlans
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
    name = "DLink.DES21xx.get_vlans"
    cache = True
    implements = [IGetVlans]
    rx_vlan = re.compile(
        r"VLAN_ID:(?P<vlanid>\d+)\n(VLAN name:(?P<vlanname>\S+)\n)*",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan", cached=True)):
            d = {}
            d["vlan_id"] = int(match.group('vlanid'))
            if match.group('vlanname'):
                d["name"] = match.group('vlanname')
            r += [d]
        return r
