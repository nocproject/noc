# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.SPS2xx.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    name = "Linksys.SPS2xx.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        a = ""
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            a = 1
        with self.configure():
            if a:
                self.cli("vlan database")
                self.cli("vlan %d" % vlan_id)
                self.cli("exit")
                self.cli("interface vlan %d" % vlan_id)
                self.cli("name %s" % name)
                self.cli("exit")
            if tagged_ports:
                ports = ""
                for port in tagged_ports:
                    if ports:
                        ports = ports + "," + port
                    else:
                        ports = port
                self.cli("interface range ethernet %s" % ports)
                self.cli("switchport trunk allowed vlan add  %d" % vlan_id)
        self.save_config()
        return True
