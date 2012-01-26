# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan %d" % vlan_id)
            self.cli("name %s" % name)
            self.cli("exit")
        self.save_config()
        return True
