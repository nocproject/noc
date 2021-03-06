# ---------------------------------------------------------------------
# HP.GbE2.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "HP.GbE2.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("/c/l2/vlan %d/ena" % vlan_id)
            self.cli("/c/l2/vlan %d/name %s" % (vlan_id, name))
            for tp in tagged_ports:
                self.cli("/c/l2/vlan %d/add %s" % (vlan_id, tp))
        self.save_config()
        return True
