# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_inventory
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
    name = "Zyxel.ZyNOS.get_inventory"
    interface = IGetInventory

    def remove_non_ascii(self, s, sub="?"):
        return "".join([i if ord(i) < 128 else sub for i in s])

    def execute(self):
        objects = []
        v = self.scripts.get_version()
        part_no = v["platform"]
        vendor = v["vendor"]
        p = {
            "type": "CHASSIS",
            "number": 1,
            "vendor": vendor,
            "description": part_no,
            "part_no": [part_no],
            "builtin": False,
        }
        if v.get("attributes", {}).get("Serial Number", ""):
            p["serial"] = v["attributes"]["Serial Number"]
        objects += [p]
        objects += self.get_transceivers()
        return objects

    def get_transceivers(self):
        def get_offset(offset):
            def wrap(x):
                return str(int(x) + offset)

            return wrap

        objects = []
        if self.match_version(version__startswith="3.90") or self.match_version(
            version__startswith="4."
        ):
            xcvr_n = get_offset(0)
            inv = self.cli("show interface transceiver *")
            rx_trans = re.compile(
                r"Port\s+:\s+(?P<number>\d+)\s+\S+\n"
                r"Vendor\s+:\s+(?P<vendor>\S+)\s*\n"
                r"Part Number\s+:\s+(?P<part_no>\S+\s*\S*)\s*\n"
                r"Serial Number\s+:\s+(?P<serial>\S+)\s*\n"
                r"Revision\s+:\s+(?P<rev>\S+)?\s*\n"
                r"Date Code\s+:\s+\S+\n"
                r"Transceiver\s+:\s+(?P<type>\S+)",
                re.MULTILINE | re.DOTALL,
            )
        else:
            if self.match_version(platform__contains="2024"):
                xcvr_n = get_offset(25)
            elif self.match_version(platform__contains="2108"):
                xcvr_n = get_offset(9)
            else:
                xcvr_n = get_offset(1)
            with self.zynos_mode():
                inv = self.cli("sys sw sfp disp")
            rx_trans = re.compile(
                r"SFP\s+:\s+(?P<number>\d+)\s*\n"
                r"Vendor\s+:\s+(?P<vendor>\S+)\s*\n"
                r"Part\sNumber\s+:\s+(?P<part_no>\S+\s*\S*)\s*\n"
                r"Series\sNumber\s+:\s+(?P<serial>\S+)\s*\n"
                r"Revision\s+:\s+(?P<rev>\S+)?\s*\n"
                r"Transceiver\s+:\s+(?P<type>\S+)",
                re.MULTILINE | re.DOTALL,
            )

        for match in rx_trans.finditer(inv):
            try:
                vendor = match.group("vendor").encode("utf-8")
            except UnicodeDecodeError:
                vendor = "NONAME"
            try:
                part_no = match.group("part_no").encode("utf-8").strip()
            except UnicodeDecodeError:
                part_no = "NoName | Transceiver | Unknown SFP"
            part_no_orig = self.remove_non_ascii(match.group("part_no").strip())
            if vendor in ["NONAME", "OEM", "CISCO-FINISAR", "AODevices"]:
                part_no = "NoName | Transceiver | "
                description = match.group("type")
                if description.endswith(tuple([" EX", "-EX"])):
                    part_no = part_no + "1G | SFP EX"
                elif description.endswith(tuple([" LH", "-LH"])):
                    part_no = part_no + "1G | SFP LH"
                elif description.endswith(tuple([" LX", "-LX"])):
                    part_no = part_no + "1G | SFP LX"
                elif description.endswith(tuple([" SX", "-SX"])):
                    part_no = part_no + "1G | SFP SX"
                elif description.endswith(tuple([" T", "-T"])):
                    part_no = part_no + "1G | SFP T"
                elif description.endswith(tuple([" TX", "-TX"])):
                    part_no = part_no + "1G | SFP TX"
                elif description.endswith(tuple([" ZX", "-ZX"])):
                    part_no = part_no + "1G | SFP ZX"
                elif part_no_orig.endswith(tuple(["BX-U", "BX-1"])):
                    part_no = part_no + "1G | SFP BXU"
                elif part_no_orig.endswith("BX-D"):
                    part_no = part_no + "1G | SFP BXD"
                else:
                    part_no = part_no + "Unknown SFP"
            revision = self.remove_non_ascii(match.group("rev"), "") if match.group("rev") else None
            o = {
                "type": "XCVR",
                "number": xcvr_n(match.group("number")),
                "vendor": vendor,
                "description": "%s (%s)" % (match.group("type"), vendor),
                "part_no": [part_no.strip()],
                "builtin": False,
            }
            if revision:
                o["revision"] = revision
            try:
                o["serial"] = match.group("serial").encode("utf-8")
            except UnicodeDecodeError:
                pass
            objects += [o]
        return objects
