# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
 
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    name = "DLink.DxS.get_switchport"
    interface = IGetSwitchport
=======
##----------------------------------------------------------------------
## DLink.DxS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "DLink.DxS.get_switchport"
    implements = [IGetSwitchport]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
<<<<<<< HEAD
                "802.1Q Enabled": True,
                "tagged": [v["vlan_id"] for v in vlans if iface in v["tagged_ports"]]
            }
            desc = p['desc']
            if desc and desc != 'null':
                i['description'] = desc
            untagged = [v["vlan_id"] for v in vlans if iface in v["untagged_ports"]]
            if untagged:
                i["untagged"] = untagged[0]
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            interfaces += [i]
        return interfaces
