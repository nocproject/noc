# ---------------------------------------------------------------------
# Force10.FTOS.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Force10.FTOS.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli(f"interface vlan {int(vlan_id)}")
            self.cli(f"name {name}")
            for tp in tagged_ports:
                self.cli(f"tagged {tp}")
            self.cli("no shutdown")
            self.cli("exit")
        self.save_config()
        return True
