# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9400.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT9400.get_vlans"
    interface = IGetVlans
    rx_vlan = re.compile(r"VLAN Name \.+ (?P<vlanname>\S+)\n VLAN ID \.+ (?P<vlanid>\d+)\n")

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r.append({
                "vlan_id": int(match.group('vlanid')),
                "name": match.group('vlanname')
            })
        return r
