# ---------------------------------------------------------------------
# Huawei.VRP3.add_vlan
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Huawei.VRP3.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("interface lan 0/0 \n")
            self.cli(f"vlan {int(vlan_id)} common\n")
            self.cli("exit\n")
            if tagged_ports:
                for port in tagged_ports:
                    self.cli(
                        f"pvc  adsl {port} 0 35 lan 0/0 {int(vlan_id)} 1 disable 1483b off off 1 1"
                    )
        self.save_config()
        return True
