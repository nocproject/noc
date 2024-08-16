# ---------------------------------------------------------------------
# VMWare.vHost.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "VMWare.vHost.get_interfaces"
    cache = True
    interface = IGetInterfaces

    def execute_controller(self, hid: str):
        h = self.vim.get_host_by_id(hid)
        interfaces = {}
        for nic in h.config.network.pnic:
            iface = {
                "name": nic.device,
                "admin_status": bool(nic.linkSpeed),
                "oper_status": bool(nic.linkSpeed),
                "mac": nic.mac,
                "type": "physical",
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            interfaces[nic.device] = iface
        return [{"interfaces": list(interfaces.values())}]

    def execute(self, **kwargs):
        return self.execute_controller(hid=self.controller.local_id)
