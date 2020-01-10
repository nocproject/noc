# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from datetime import datetime

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Qtech.QSW2800.get_inventory"
    interface = IGetInventory

    rx_trans = re.compile(
        r"Transceiver info:\n"
        r"\s+SFP found in this port, manufactured by\s+(?P<vendor>.+?), on\s+(?P<mfg_date>.+)\.\n"
        r"\s+Type is\s+(?P<sfp_type>.+)\.\s+Serial number is\s+(?P<serial_number>.+)\.\n"
        r"\s+Link length is\s+(?P<link_length>.+) for\s+(?P<fiber_mode>.+)\.\n"
        r"\s+Nominal bit rate is\s+(?P<bit_rate>.+)\.\n"
        r"\s+Laser wavelength is\s+(?P<wavelength>.+)\.",
        re.MULTILINE | re.IGNORECASE,
    )

    rx_iface_split = re.compile(r"Interface brief:\n", re.IGNORECASE)
    rx_eth_member = re.compile(r"Ethernet(?P<member>\d+)/0/\d+")
    rx_member = re.compile(
        r"^Hardware version\s+: (?P<revision>\S+)\s*\n"
        r"^Serial number\s+: (?P<serial>\S+)\s*\n"
        r"^Manufacture date\s+: (?P<mfg_date>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = {"type": "CHASSIS", "number": "1", "vendor": "QTECH"}
        v = self.scripts.get_version()
        if "platform" not in v:
            return []
        r["part_no"] = v["platform"]
        if "attributes" in v:
            r["serial"] = v["attributes"]["Serial Number"]
            if "HW version" in v["attributes"]:
                r["revision"] = v["attributes"]["HW version"]
        if self.is_stackable:
            try:
                c = self.cli("show member 1 slot 1")
                match = self.rx_member.search(c)
                if match:
                    r["serial"] = match.group("serial")
                    r["revision"] = match.group("revision")
                    r["mfg_date"] = match.group("mfg_date").replace("/", "-")
            except self.CLISyntaxError:
                pass
        r = [r]
        old_member = 1
        v = self.cli("show interface")
        for iface in self.rx_iface_split.split(v):
            if not iface:
                continue
            num = iface.split()[0].split("/")[-1]
            if self.is_stackable:
                match = self.rx_eth_member.search(iface)
                if match:
                    member = int(match.group("member"))
                    if member > old_member:
                        ch = {
                            "type": "CHASSIS",
                            "number": member,
                            "vendor": "QTECH",
                            "part_no": r[0]["part_no"],
                        }
                        try:
                            c = self.cli("show member %d slot 1" % member)
                            match = self.rx_member.search(c)
                            if match:
                                ch["serial"] = match.group("serial")
                                ch["revision"] = match.group("revision")
                                ch["mfg_date"] = match.group("mfg_date").replace("/", "-")
                        except self.CLISyntaxError:
                            pass
                        r += [ch]
                        old_member = member
            for t in self.rx_trans.finditer(iface):
                part_no = self.profile.convert_sfp(
                    t.group("sfp_type"),
                    t.group("link_length"),
                    t.group("bit_rate"),
                    t.group("wavelength"),
                )
                data = {
                    "type": "XCVR",
                    "number": num,
                    "vendor": t.group("vendor").strip(),
                    "part_no": part_no,
                    "serial": t.group("serial_number").strip(),
                    "description": "",
                }
                try:
                    mfg_date = datetime.strptime(t.group("mfg_date"), "%b %d %Y")
                    data["mfg_date"] = mfg_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
                r += [data]

        return r
