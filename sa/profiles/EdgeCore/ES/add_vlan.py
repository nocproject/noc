# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "EdgeCore.ES.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan database")
            self.cli("vlan %d name %s m e s a" % (vlan_id, name))
            self.cli("end")
            if tagged_ports:
                for port in tagged_ports:
                    self.cli("interface eth %s" % port)
                    self.cli("switchport allowed vlan add %s tagged" % vlan_id)
                    self.cli("end")
        return True
