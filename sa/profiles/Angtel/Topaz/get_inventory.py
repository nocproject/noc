# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Angtel.Topaz.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Angtel.Topaz.get_inventory"
    cache = True
    interface = IGetInventory

    rx_port = re.compile(
        r"^(?P<port>(?:Fa|Gi|Te|Po)\S+)\s+(?P<type>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(?:Up|Down|Not Present)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_sfp_vendor = re.compile(r"SFP vendor name:(?P<vendor>\S+)")
    rx_sfp_serial = re.compile(r"SFP serial number:(?P<serial>\S+)")

    def execute_cli(self):
        v = self.scripts.get_version()
        c = {"type": "CHASSIS", "vendor": "ANGTEL", "part_no": v["platform"]}
        if "HW version" in v["attributes"]:
            c["revision"] = v["attributes"]["HW version"]
        if "Serial Number" in v["attributes"]:
            c["serial"] = v["attributes"]["Serial Number"]
        r = [c]
        v = self.cli("show interfaces status", cached=True)
        for match in self.rx_port.finditer(v):
            if match.group("type") in ["1G-Combo-C", "1G-Combo-F", "10G-Combo-C", "10G-Combo-F"]:
                c = self.cli(
                    "show fiber-ports optical-transceiver interface %s" % match.group("port")
                )
                match1 = self.rx_sfp_serial.search(c)
                if match1:
                    r += [
                        {
                            "type": "XCVR",
                            "vendor": "NONAME",
                            "part_no": "Unknown | Transceiver | SFP",
                            "number": match.group("port")[-1:],
                            "serial": match1.group("serial"),
                        }
                    ]
        return r
