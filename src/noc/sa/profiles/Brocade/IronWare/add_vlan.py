# ---------------------------------------------------------------------
# Brocade.IronWare.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Brocade.IronWare.add_vlan"
    interface = IAddVlan

    def execute_cli(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli(f"vlan {int(vlan_id)} name {name}")
            if tagged_ports:
                self.cli("tagged " + " ".join(tagged_ports))
            self.cli("exit")
        self.save_config()
        return True
