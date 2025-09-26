# ---------------------------------------------------------------------
# SKS.SKS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_table


class Script(BaseScript):
    name = "SKS.SKS.get_inventory"
    interface = IGetInventory
    cache = True

    rx_e1_part_no = re.compile(r"^sysType\s+(?P<part_no>.+?)\s*\n", re.MULTILINE)
    rx_e1_serial = re.compile(r"^serialNum\s+(?P<serial>\S+)\s*\n", re.MULTILINE)
    rx_e1_revision = re.compile(r"^hwVer\s+(?P<revision>\S+)\s*\n", re.MULTILINE)
    rx_port1 = re.compile(
        r"^(?P<port>(?:Fa|Gi|Te|Po)\S+)\s+(?P<type>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(?:Up|Down|Not Present)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_port2 = re.compile(r"^(?P<port>[fgt]\d\S*)\s+.+?\s+(?P<type>\S+)\s*\n", re.MULTILINE)
    rx_sfp_vendor = re.compile(r"SFP vendor name:(?P<vendor>\S+)")
    rx_sfp_serial = re.compile(r"SFP serial number:(?P<serial>\S+)")

    def get_e1_inventory(self):
        v = self.cli("?", command_submit=b"")
        if "enter E1 context" in v:
            with self.profile.e1(self):
                v = self.cli("info")
                if "E1 functionality is disabled." in v:
                    return []
                part_no = self.rx_e1_part_no.search(v)
                if part_no:
                    part_no = part_no.group("part_no")
                else:
                    # If no module data
                    return []
                serial = self.rx_e1_serial.search(v).group("serial")
                revision = self.rx_e1_revision.search(v).group("revision")
                return [
                    {
                        "type": "MODULE",
                        "vendor": "SKS",
                        "part_no": part_no,
                        "serial": serial,
                        "revision": revision,
                    }
                ]
        return []

    def execute(self):
        v = self.cli("show version", cached=True)
        if "Unit" in v:
            stack = {}
            r = []
            t = parse_table(v)
            for i in t:
                stack[i[0]] = {"type": "CHASSIS", "vendor": "SKS", "revision": i[3]}
            v = self.cli("show system", cached=True)
            t = parse_table(v, footer=r"Unit\s+Temperature")
            for i in t:
                platform = i[1]
                if platform == "SKS 10G":
                    platform = "SKS-16E1-IP-1U"
                elif platform.startswith("SKS"):
                    platform = "SKS-16E1-IP"
                if not i[0]:
                    break
                stack[i[0]]["part_no"] = platform
            v = self.cli("show system id", cached=True)
            t = parse_table(v)
            for i in t:
                stack[i[0]]["serial"] = i[1]
            for i in stack:
                r += [stack[i]]
            return r
        v = self.scripts.get_version()
        r = [
            {
                "type": "CHASSIS",
                "vendor": "SKS",
                "part_no": v["platform"],
            }
        ]
        serial = self.capabilities.get("Chassis | Serial Number")
        revision = self.capabilities.get("Chassis | HW Version")
        if serial:
            r[0]["serial"] = serial
        if revision:
            r[0]["revision"] = revision
        r += self.get_e1_inventory()
        try:
            v = self.cli("show interfaces status", cached=True)
            rx_port = self.rx_port1
        except self.CLISyntaxError:
            v = self.cli("show interface brief")
            rx_port = self.rx_port2
        for match in rx_port.finditer(v):
            if match.group("type") in [
                "1G-Combo-C",
                "1G-Combo-F",
                "10G-Combo-C",
                "10G-Combo-F",
                "Giga-Combo-TX",
                "Giga-Combo-FX",
            ]:
                try:
                    c = self.cli(
                        "show fiber-ports optical-transceiver interface %s" % match.group("port")
                    )
                except self.CLISyntaxError:
                    break
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
