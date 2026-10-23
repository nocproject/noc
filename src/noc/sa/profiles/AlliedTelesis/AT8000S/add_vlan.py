# ---------------------------------------------------------------------
# AlliedTelesis.AT8000S.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "AlliedTelesis.AT8000S.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        has_vlan = self.scripts.has_vlan(vlan_id=vlan_id)
        with self.configure():
            if not has_vlan:
                self.cli("vlan database")
                self.cli(f"vlan {int(vlan_id)}")
                self.cli("exit")
                self.cli(f"interface vlan {int(vlan_id)}")
                self.cli(f"name {name}")
                self.cli("exit")
            for p in tagged_ports:
                self.cli(f"interface ethernet {p}")
                self.cli("switchport mode general")
                self.cli(f"switchport general allowed vlan add {int(vlan_id)}")
                self.cli("exit")
        self.save_config()
        return True
