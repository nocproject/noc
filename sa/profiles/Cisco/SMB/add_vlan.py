# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.add_vlan
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

#  NOC module
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Cisco.SMB.add_vlan"
    interface = IAddVlan

    def execute_cli(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("interface vlan %d" % vlan_id)
            self.cli("name %s" % name)
            self.cli("exit")
        self.save_config()
        return True
