# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    name = "DLink.DxS.get_switchport"
    interface = IGetSwitchport

    def execute(self):

        ports = self.profile.get_ports(self)
        vlans = self.profile.get_vlans(self)
        interfaces = []

        for p in ports:
            iface = p['port']
            i = {
                "interface": iface,
                "status": p['status'],
                "members": [],
                "802.1Q Enabled": True
            }
            desc = p['desc']
            if desc != '' and desc != 'null':
                i['description'] = desc
            tagged_vlans = []
            for v in vlans:
                if iface in v['tagged_ports']:
                    tagged_vlans += [v['vlan_id']]
                if iface in v['untagged_ports']:
                    i['untagged'] = v['vlan_id']
            i['tagged'] = tagged_vlans
            interfaces += [i]
        return interfaces
