# ---------------------------------------------------------------------
# Alcatel.7302.get_inventory
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
    name = "Alcatel.7302.get_inventory"
    interface = IGetInventory

    rx_split = re.compile(
        r"^slot\s*\n^-{100,}\s*\n(?P<data>(?:.+\n)+?)^-{100,}\s*\n",
        re.MULTILINE,
    )
    rx_slot_no = re.compile(r"\s+slot : (?P<slot_no>\S+)")
    rx_slot_type = re.compile(r"\s+actual-type : (?P<slot_type>\S+)")
    rx_serial = re.compile(r"\s+serial-no : (?P<serial>\S+)")
    port_map = {
        7: "7330",
        10: "7330",
        11: "7330",
        14: "7330",
        17: "7342",
        18: "7302",
        19: "7302",
        21: "7302",
    }  # show equipment slot for 7302 with one control plate return 19 slots

    def execute_cli(self, **kwargs):
        r = []
        v = self.scripts.get_version()
        r += [{"type": "CHASSIS", "vendor": "ALCATEL", "part_no": [v["platform"]]}]
        v = self.cli("show equipment slot detail")
        for c in self.rx_split.finditer(v):
            data = c.group("data")
            match = self.rx_slot_no.search(data)
            if not match:
                continue
            slot_no = match.group("slot_no")
            if slot_no.startswith("1/1/") or slot_no.startswith("lt:1/1/"):
                slot_no = slot_no.split("/")[-1]
            match = self.rx_slot_type.search(data)
            if not match:
                continue
            slot_type = match.group("slot_type").upper()
            if slot_type == "EMPTY":
                continue
            slot = {
                "type": "LINECARD",
                "vendor": "ALCATEL",
                "number": slot_no,
                "part_no": [slot_type],
            }
            match = self.rx_serial.search(data)
            if match:
                slot["serial"] = match.group("serial").replace('"', "")
            r += [slot]

        return r

    def execute_snmp(self, **kwargs):
        r = []
        slots = 0
        for b_index, b_type, b_revision, b_serial in self.snmp.get_tables(
            [
                "1.3.6.1.4.1.637.61.1.23.3.1.3",
                "1.3.6.1.4.1.637.61.1.23.3.1.17",
                "1.3.6.1.4.1.637.61.1.23.3.1.19",
            ]
        ):
            slots += 1
            if b_type == "EMPTY":
                continue
            r += [{"number": slots, "type": "LINECARD", "vendor": "Alcatel", "part_no": b_type}]
            if b_serial is not None:
                sn = b_serial.strip().strip("\x00")
                r[-1]["serial"] = sn
            if b_revision is not None:
                r[-1]["revision"] = b_revision
        platform = self.port_map[slots]
        v = self.snmp.get("1.3.6.1.4.1.637.61.1.23.2.1.3.1")
        if v in ["LEEU", "LEUS", "MLSA"]:
            platform = platform + "XD"
        elif v == "LNEU":
            platform = platform + "FD"
        r.insert(
            0,
            {
                "number": "0",
                "type": "CHASSIS",
                "vendor": "Alcatel",
                "part_no": platform,
            },
        )
        return r
