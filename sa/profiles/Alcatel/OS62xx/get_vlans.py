# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans

class Script(noc.sa.script.Script):
    name="Alcatel.OS62xx.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        vlans=self.cli("show vlan")
        r=[]
        in_body=False
        for l in vlans.split("\n"):
            l=l.strip()
            if not in_body:
                if l.startswith("----"):
                    in_body=True
                continue
            try:
                vlan_id,name,ports,vlan_type,auth=l.split()
            except:
                continue
            r.append({"vlan_id":int(vlan_id),"name":name})
        return r
