# ---------------------------------------------------------------------
# Eltex.MA4000.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MA4000.get_inventory"
    interface = IGetInventory

    rx_serial = re.compile(r"^\s+Serial number: (?P<serial>\S+)", re.MULTILINE)
    rx_slot = re.compile(
        r"^\s*Module type:\s+(?P<part_no>\S+)\s*\n"
        r"^\s*Hardware version:\s+(?P<revision>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_gpon_port = re.compile(r"^\s*Gpon-port:\s+(.+)\n", re.MULTILINE)
    rx_gpon_vendor = re.compile(r"^\s*SFP vendor:\s+(.+)\n", re.MULTILINE)
    rx_gpon_part_no = re.compile(r"^\s*SFP product number:\s+(.+)\n", re.MULTILINE)
    rx_gpon_rev = re.compile(r"^\s*SFP vendor revision:\s+(.+)\n", re.MULTILINE)
    rx_sep = re.compile(r"\s\s+")

    def execute_cli(self, **kwargs):
        res = [
            {
                "type": "CHASSIS",
                "vendor": "ELTEX",
                "part_no": "MA4000",
            }
        ]
        for i in [1, 2]:
            v = self.cli(f"show system information {int(i)}", cached=True)
            match = self.rx_serial.search(v)
            if match:
                r = {
                    "type": "SUP",
                    "number": i,
                    "vendor": "ELTEX",
                    "serial": match.group("serial"),
                    "part_no": "PP4X",
                }
                res.append(r)
        v = self.cli("show shelf")
        for i in parse_table(v):
            if i[2] == "none":
                continue
            c = self.cli(f"show slot {i[0]} information")
            match = self.rx_slot.search(c)
            if i[1] == "none" and i[2] == "plc8":
                r = {
                    "type": "LINECARD",
                    "number": i[0],
                    "vendor": "ELTEX",
                    "serial": i[4],
                    "part_no": "PLC8",
                }
            else:
                r = {
                    "type": "LINECARD",
                    "number": i[0],
                    "vendor": "ELTEX",
                    "serial": i[4],
                    "part_no": match.group("part_no"),
                    "revision": match.group("revision"),
                }
            res.append(r)
            sfp = []
            c = self.cli(f"show interface gpon-port {i[0]}/all state")
            match = self.rx_gpon_port.search(c)
            if not match:
                continue
            items = self.rx_sep.split(match.group(1))
            for i in range(64):  # Maximum value
                try:
                    sfp.append({"number": items[i].strip(), "type": "XCVR"})
                except IndexError:
                    break
            sfp_count = i
            match = self.rx_gpon_vendor.search(c)
            items = self.rx_sep.split(match.group(1))
            for i in range(sfp_count):
                sfp[i]["vendor"] = items[i].strip()
            match = self.rx_gpon_part_no.search(c)
            items = self.rx_sep.split(match.group(1))
            for i in range(sfp_count):
                sfp[i]["part_no"] = items[i].strip()
            match = self.rx_gpon_rev.search(c)
            items = self.rx_sep.split(match.group(1))
            for i in range(sfp_count):
                sfp[i]["revision"] = items[i].strip()
            for i in range(sfp_count):
                res.append(sfp[i])
        return res
