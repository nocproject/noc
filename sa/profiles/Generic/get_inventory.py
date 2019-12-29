# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Generic.get_inventory"
    interface = IGetInventory

    def get_inv_from_version(self):
        v = self.scripts.get_version()
        serial = None
        if "attributes" in v and "Serial Number" in v["attributes"]:
            serial = v["attributes"]["Serial Number"]
        revision = None
        if "attributes" in v and "HW version" in v["attributes"]:
            revision = v["attributes"]["HW version"]

        return [
            {
                "type": "CHASSIS",
                "vendor": v["vendor"],
                "part_no": [v["platform"]],
                "serial": serial,
                "revision": revision,
            }
        ]

    def execute_snmp(self):
        return self.get_inv_from_version()

    def execute_cli(self):
        return self.get_inv_from_version()
