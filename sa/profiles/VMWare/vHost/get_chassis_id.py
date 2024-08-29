# ---------------------------------------------------------------------
# VMWare.vHost.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from ..vim import VIMScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(VIMScript):
    name = "VMWare.vHost.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_controller(self, hid: str):
        h = self.vim.get_host_by_id(hid)
        r = []
        for v_nic in h.config.network.vnic:
            if not v_nic.spec.mac:
                continue
            r.append({"first_chassis_mac": v_nic.spec.mac, "last_chassis_mac": v_nic.spec.mac})
        return r

    def execute(self, **kwargs):
        return self.execute_controller(hid=self.controller.local_id)
