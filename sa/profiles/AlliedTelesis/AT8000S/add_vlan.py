# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        has_vlan = self.scripts.has_vlan(vlan_id=vlan_id)
        with self.configure():
            if not has_vlan:
                self.cli("vlan database")
                self.cli("vlan %d" % vlan_id)
                self.cli("exit")
                self.cli("interface vlan %d" % vlan_id)
                self.cli("name %s" % name)
                self.cli("exit")
            for p in tagged_ports:
                self.cli("interface ethernet %s" % p)
                self.cli("switchport mode general")
                self.cli("switchport general allowed vlan add %d" % vlan_id)
                self.cli("exit")
        self.save_config()
        return True
