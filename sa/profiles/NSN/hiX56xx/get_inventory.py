# ---------------------------------------------------------------------
# NSN.hiX56xx.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "NSN.hiX56xx.get_inventory"
    interface = IGetInventory

    def execute_cli(self):
        v = self.scripts.get_version()
        serial = self.capabilities.get("Chassis | Serial Number")
        revision = self.capabilities.get("Chassis | HW Version")
        if serial:
            serial = serial
        if revision:
            revision = revision

        r = [
            {
                "type": "CHASSIS",
                "vendor": v["vendor"],
                "part_no": [v["platform"]],
                "serial": serial,
                "revision": revision,
            }
        ]
        part_no = ""
        number = ""
        serial = ""
        revision = ""
        v = self.cli("show slot-overview")
        for line in v.splitlines():
            s = line.split("|")
            if len(s) < 2 or s[1].startswith("=") or s[1].startswith(" Slot "):
                continue
            if s[1].startswith("-"):
                if part_no:
                    r += [
                        {
                            "type": "LINECARD",
                            "vendor": "NSN",
                            "part_no": part_no,
                            "number": number,
                            "serial": serial,
                            "revision": revision,
                        }
                    ]
                part_no = ""
                number = ""
                serial = ""
                revision = ""
            else:
                part_no = part_no + s[3].strip()
                number = number + s[1].strip()
                serial = serial + s[8].strip()
                revision = revision + s[7].strip()

        return r
