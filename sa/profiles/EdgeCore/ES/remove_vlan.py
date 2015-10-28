# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iremovevlan import IRemoveVlan


class Script(BaseScript):
    name = "EdgeCore.ES.remove_vlan"
    interface = IRemoveVlan

    def execute(self, vlan_id, tagged_ports):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("vlan database")
            self.cli("no vlan %d" % vlan_id)
            self.cli("end")
            if tagged_ports:
                for port in tagged_ports:
                    self.cli("interface eth %d" % port)
                    self.cli("switchport allowed vlan remove %d" % vlan_id)
                    self.cli("end")
        return True
