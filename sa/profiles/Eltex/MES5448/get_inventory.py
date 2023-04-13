# ---------------------------------------------------------------------
# Eltex.MES5448.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES5448.get_inventory"
    interface = IGetInventory

    def execute_cli(self, **kwargs):
        v = self.scripts.get_version()
        res = [
            {
                "type": "CHASSIS",
                "vendor": "ELTEX",
                "part_no": v["platform"],
            }
        ]
        serial = self.capabilities.get("Chassis | Serial Number")
        if serial:
            res[-1]["serial"] = serial
        revision = self.capabilities.get("Chassis | HW Version")
        if revision:
            res[-1]["revision"] = revision
        try:
            v = self.cli("show fiber-ports optical-transceiver-info all")
            for i in parse_table(v, line_wrapper=None):
                r = {
                    "type": "XCVR",
                    "number": i[0].split("/")[-1],
                    "vendor": i[2],
                    "serial": i[5],
                    "part_no": i[6],
                }
                if i[2] == "OEM":
                    if i[9] in ["1000LX", "1GBase-LX"]:
                        r["part_no"] = "NoName | Transceiver | 1G | SFP LX"
                    elif i[9] in ["1GBase-BX10"]:  # Only BX10U and BX10D exist
                        r["part_no"] = "NoName | Transceiver | 1G | SFP"
                    elif i[9] in ["1GBase-T"]:
                        r["part_no"] = "NoName | Transceiver | 1G | SFP T"
                    elif i[9] == "10GBase-SR":
                        r["part_no"] = "NoName | Transceiver | 10G | SFP+ SR"
                    elif i[9] == "10GBase-LR":
                        r["part_no"] = "NoName | Transceiver | 10G | SFP+ LR"
                    elif i[9] == "10GBase-ER":
                        r["part_no"] = "NoName | Transceiver | 10G | SFP+ ER"
                    else:
                        raise self.NotSupportedError()
                if i[8]:
                    r["revision"] = i[8]
                res += [r]
        except self.CLISyntaxError:
            pass

        return res
