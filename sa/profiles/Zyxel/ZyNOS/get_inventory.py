# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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
    keep_cli_session = False

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
        serial = self.capabilities.get("Chassis | Serial Number")
        if serial:
            p["serial"] = serial
        objects += [p]
        objects += self.get_transceivers()
        return objects

    def get_transceivers(self):
        def get_offset(offset):
            def wrap(x):
                return str(int(x) + offset)

            return wrap

        objects = []
        if self.is_version_3_90 or self.is_version_4_xx:
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
            if self.is_platform_2024:
                xcvr_n = get_offset(25)
            elif self.is_platform_2108:
                xcvr_n = get_offset(9)
            else:
                xcvr_n = get_offset(1)
            with self.zynos_mode():
                inv = self.cli("sys sw sfp disp")
            rx_trans = re.compile(
                r"SFP\s+:\s+(?P<number>\d+)\s*\n"
                r"Vendor\s+:\s+(?P<vendor>\S+)?\s*\n"
                r"Part\sNumber\s+:\s+(?P<part_no>\S+\s*\S*)?\s*\n"
                r"Series\sNumber\s+:\s+(?P<serial>\S+)?\s*\n"
                r"Revision\s+:\s+(?P<rev>\S+)?\s*\n"
                r"Transceiver\s+:\s+(?P<type>\S+)",
                re.MULTILINE | re.DOTALL,
            )

        for match in rx_trans.finditer(inv):
            vendor = "NONAME"
            part_no = "NoName | Transceiver | Unknown SFP"
            part_no_orig = ""
            if match.group("vendor"):
                vendor = match.group("vendor").strip()
            if match.group("part_no"):
                part_no = match.group("part_no").strip()
                part_no_orig = self.remove_non_ascii(match.group("part_no").strip())
            if vendor in ["NONAME", "OEM", "CISCO-FINISAR", "AODevices"]:
                part_no = "NoName | Transceiver | "
                description = match.group("type")
                if description.endswith((" EX", "-EX")):
                    part_no = part_no + "1G | SFP EX"
                elif description.endswith((" LH", "-LH")):
                    part_no = part_no + "1G | SFP LH"
                elif description.endswith((" LX", "-LX")):
                    part_no = part_no + "1G | SFP LX"
                elif description.endswith((" SX", "-SX")):
                    part_no = part_no + "1G | SFP SX"
                elif description.endswith((" T", "-T")):
                    part_no = part_no + "1G | SFP T"
                elif description.endswith((" TX", "-TX")):
                    part_no = part_no + "1G | SFP TX"
                elif description.endswith((" ZX", "-ZX")):
                    part_no = part_no + "1G | SFP ZX"
                elif part_no_orig.endswith(("BX-U", "BX-1")):
                    part_no = part_no + "1G | SFP BXU"
                elif part_no_orig.endswith("BX-D"):
                    part_no = part_no + "1G | SFP BXD"
                else:
                    part_no = part_no + "Unknown SFP"
            description = "%s (%s)" % (match.group("type"), vendor)
            if part_no_orig:
                description = "%s (p/n: %s)" % (description, part_no_orig)
            o = {
                "type": "XCVR",
                "number": xcvr_n(match.group("number")),
                "vendor": vendor,
                "description": description,
                "part_no": [part_no.strip()],
                "builtin": False,
            }
            revision = self.remove_non_ascii(match.group("rev"), "") if match.group("rev") else None
            if revision:
                o["revision"] = revision
            serial_no = (
                self.remove_non_ascii(match.group("serial"), "") if match.group("serial") else None
            )
            if serial_no:
                o["serial"] = serial_no
            objects += [o]
        return objects
