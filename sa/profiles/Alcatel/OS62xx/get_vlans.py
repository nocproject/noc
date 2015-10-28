# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Alcatel.OS62xx.get_vlans"
    interface = IGetVlans

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        in_body = False
        for l in vlans.split("\n"):
            l = l.strip()
            if not in_body:
                if l.startswith("----"):
                    in_body = True
                continue
            try:
                vlan_id, name, ports, vlan_type, auth = l.split()
            except:
                continue
            r.append({"vlan_id": int(vlan_id), "name": name})
        return r
