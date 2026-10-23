# ---------------------------------------------------------------------
# EdgeCore.ES.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "EdgeCore.ES.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan database")
            self.cli(f"vlan {int(vlan_id)} name {name} m e s a")
            self.cli("end")
            if tagged_ports:
                for port in tagged_ports:
                    self.cli(f"interface eth {port}")
                    self.cli(f"switchport allowed vlan add {vlan_id} tagged")
                    self.cli("end")
        return True
