# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IAddVlan


class Script(BaseScript):
    name = "Cisco.IOS.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan %d" % vlan_id)
            self.cli("name %s" % name)
            self.cli("exit")
        self.save_config()
        return True
