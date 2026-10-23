# ----------------------------------------------------------------------
# Alcatel.AOS.add_vlan
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Alcatel.AOS.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli(f"vlan {int(vlan_id)} enable name {name}")
            if tagged_ports:
                for port in tagged_ports:
                    self.cli(f"vlan {int(vlan_id)} 802.1q 1/{port}")
        self.save_config()
        return True
