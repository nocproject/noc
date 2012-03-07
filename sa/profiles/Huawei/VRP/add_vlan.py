# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    name = "Huawei.VRP.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan %d" % vlan_id)
            self.cli("description %s" % name)
            self.cli("quit")
        self.save_config()
        return True
