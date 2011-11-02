# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IAddVlan

class Script(noc.sa.script.Script):
    name = "Eltex.MES.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        a = ''
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            a = 1;
        with self.configure():
            if a:
                self.cli("vlan database")
                self.cli("vlan %d"%vlan_id)
                self.cli("exit")
                self.cli("interface vlan %d"%vlan_id)
                self.cli("name %s"%name)
                self.cli("exit")
            if tagged_ports:
                ports = ''
                for port in tagged_ports:
                    if ports:
                        ports = ports + ',' + port
                    else:
                        ports = port
                self.cli("interface range %s"%ports)
### 802.1q
#                self.cli("switchport general allowed vlan add %d tagged"%vlan_id)
## trunk
                self.cli("switchport trunk allowed vlan add  %d"%vlan_id)
        self.save_config()
        return True
