# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import re
## Python modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans

rx_vlan = re.compile(r"^(?P<interface>\S+)\s+\|+\s+(?P<vlan>\d+)\s+\|+\s+\S+$", re.MULTILINE)

class Script(NOCScript):
    name = "OS.Linux.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        r = []
        for vlan in rx_vlan.finditer(self.cli("cat /proc/net/vlan/config")):
            vlan_id = vlan.group("vlan")
# TODO vlan name... Looking for way find vlan name in GNU/Linux and *BSD
            name = 'br' + vlan_id
            if {"vlan_id" : vlan_id, "name" : name } not in r:
                r.append( {
                            "vlan_id" : vlan_id,
                            "name"    : name,
                            } )
        if not r:
            raise Exception("Not implemented")
        return r
