# ---------------------------------------------------------------------
# DLink.DES21xx.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "DLink.DES21xx.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        v = self.scripts.get_version()
        cmd = f"create vlan tag {int(vlan_id)}"
        if v["version"][0] >= "5":  # sofrware version 5.0.0 or above
            cmd += f" desc {name}"
        with self.configure():
            self.cli(cmd)
            if tagged_ports:
                for port in tagged_ports:
                    if v["version"][0] >= "5":
                        cmd = f"config vlan vid {int(vlan_id)} add tagged {port}"
                    else:
                        cmd = f"config vlan tag {int(vlan_id)} add tagged {port}"
                    self.cli(cmd)
        self.save_config()
        return True
