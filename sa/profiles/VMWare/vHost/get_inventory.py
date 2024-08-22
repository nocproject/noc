# ---------------------------------------------------------------------
# VMWare.vHost.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "VMWare.vHost.get_inventory"
    interface = IGetInventory

    def execute_controller(self, hid: str):
        h = self.vim.get_host_by_id(hid)
        serial = h.hardware.systemInfo.serialNumber
        if not serial:
            for info in h.hardware.systemInfo.otherIdentifyingInfo:
                if info.identifierValue:
                    serial = info.identifierValue
                    break
        return [
            {
                "type": "CHASSIS",
                "vendor": h.hardware.systemInfo.vendor,
                "part_no": h.hardware.systemInfo.model,
                "serial": serial,
                "revision": h.hardware.biosInfo.biosVersion,
            }
        ]

    def execute(self, **kwargs):
        return self.execute_controller(hid=self.controller.local_id)
