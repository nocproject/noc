# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Alstec.24xx.get_inventory"
    interface = IGetInventory
    port_map = {10: "1", 18: "2", 26: "3"}  # 16, 2  # 8, 2  # 24, 2

    def execute_snmp(self, **kwargs):
        platform = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.3.0")
        serial = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.4.0")
        revision = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.14.0")
        port_num = self.snmp.get("1.3.6.1.2.1.2.1.0")
        if port_num in self.port_map:
            platform = "%s-0%s" % (platform, self.port_map[port_num])
        if not platform:
            raise NotImplementedError
        r = {
            "type": "CHASSIS",
            "vendor": "Alstec",
            "part_no": platform,
        }
        if serial and len(serial) > 5:
            r["serial"] = serial
        if revision:
            r["revision"] = revision
        return [r]
