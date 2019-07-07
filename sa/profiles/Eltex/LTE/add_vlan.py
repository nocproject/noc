# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Eltex.LTE.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.profile.switch(self):
            self.cli("configure")
            self.cli("vlan %d" % vlan_id)
            if name:
                self.cli("name %s" % name)
            if tagged_ports:
                for port in tagged_ports:
                    self.cli("tagged %s" % port)
            self.cli("exit")
            self.cli("exit")
        self.save_config()
        return True
