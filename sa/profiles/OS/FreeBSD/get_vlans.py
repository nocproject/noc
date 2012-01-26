# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_vlans
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
    name = "OS.FreeBSD.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(r"vlan: (?P<vlanid>\d+) parent interface: (?P<iface>\S+)", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("ifconfig", cached=True)):
            r += [{
                "vlan_id": int(match.group('vlanid')),
                "name": match.group('iface') + "." + match.group('vlanid'),
                }]
        return r
