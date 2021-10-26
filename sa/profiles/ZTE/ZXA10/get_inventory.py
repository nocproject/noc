# ---------------------------------------------------------------------
# ZTE.ZXA10.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "ZTE.ZXA10.get_inventory"
    interface = IGetInventory

    type = {
        "PRSF": "PWR",
        "PRVR": "PWR",
        "PRWG": "PWR",
        "PRWGS": "PWR",
        "PRWH": "PWR",
        "PUMD": "PWR",
        "SCTM": "MAINBOARD",
        "SCXL": "MAINBOARD",
        "SCXM": "MAINBOARD",
        "SCXN": "MAINBOARD",
        "SFUQ": "MAINBOARD",
        "SMXA": "MAINBOARD",
        "SPUF": "MAINBOARD",
        "GMPA": "MAINBOARD",
        "GMRA": "MAINBOARD",
        "GFCL": "LINECARD",
        "GFGL": "LINECARD",
        "GUFQ": "LINECARD",
        "GUTQ": "LINECARD",
        "GUSQ": "LINECARD",
        "GTGHK": "LINECARD",
        "GTGOG": "LINECARD",
        "GTGQ": "LINECARD",
        "HUGQ": "LINECARD",
        "HUTQ": "LINECARD",
        "HUVQ": "LINECARD",
        "VDWVD": "LINECARD",
        "GVGO": "LINECARD",
        "PTWV": "LINECARD",
        "PTWVN": "LINECARD",
        "XFTO": "LINECARD",
        "FUMO": "FAN",
        "CVST": "unknown",
        "FCSDA": "unknown",
        "FCRDC": "unknown",
        "SVWMC": "unknown",
    }
    rx_platform = re.compile(r"^\d+\s+(?P<platform>\S+)MBRack\s+.+\n", re.MULTILINE)
    rx_card = re.compile(
        r"^Real-Type\s+:\s+(?P<type>\S+)\s+Serial-Number\s+:(?P<serial>.*)\n", re.MULTILINE
    )
    rx_card2 = re.compile(
        r"^CardName\s+:\s+(?P<type>\S+)\s*\n"
        r"^Status\s+:\s+\S+\s*\n"
        r"^Port-Number\s+:\s+\d+\s*\n"
        r"^Serial-Number\s+:(?P<serial>.*)\n",
        re.MULTILINE,
    )
    rx_detail = re.compile(r"Hardware-VER\s+:\s+(?P<hardware>\S+)\s*\n", re.MULTILINE)

    def execute_cli(self):
        v = self.scripts.get_version()
        r = [{"type": "CHASSIS", "vendor": "ZTE", "part_no": [v["platform"]]}]
        if "attributes" in v:
            r[0]["serial"] = v["attributes"]["Serial Number"]
        ports = self.profile.fill_ports(self)
        for p in ports:
            v = self.cli("show card shelfno %s slotno %s" % (p["shelf"], p["slot"]))
            match = self.rx_card.search(v)
            if not match:
                match = self.rx_card2.search(v)
                if not match:
                    continue
            i = {
                "type": self.type[match.group("type")],
                "number": p["slot"],
                "vendor": "ZTE",
                "part_no": [match.group("type")],
            }
            if match.group("serial").strip():
                i["serial"] = match.group("serial").strip()
            match = self.rx_detail.search(v)
            if match and match.group("hardware") != "N/A":
                i["revision"] = match.group("hardware")
            r += [i]
        return r
