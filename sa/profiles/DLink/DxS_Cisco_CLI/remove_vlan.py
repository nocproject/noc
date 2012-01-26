# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IRemoveVlan


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.remove_vlan"
    implements = [IRemoveVlan]

    def execute(self, vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("no vlan %d" % vlan_id)
        self.save_config()
        return True
