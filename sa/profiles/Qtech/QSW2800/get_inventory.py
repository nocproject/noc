# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import datetime
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Qtech.QSW2800.get_inventory"
    interface = IGetInventory

    rx_trans = re.compile(r"Transceiver info:\n"
                          r"\s+SFP found in this port, manufactured by\s+(?P<vendor>.+?), on\s+(?P<mfg_date>.+)\.\n"
                          r"\s+Type is\s+(?P<sfp_type>.+)\.\s+Serial number is\s+(?P<serial_number>.+)\.\n"
                          r"\s+Link length is\s+(?P<link_length>.+) for\s+(?P<fiber_mode>.+)\.\n"
                          r"\s+Nominal bit rate is\s+(?P<bit_rate>.+)\.\n"
                          r"\s+Laser wavelength is\s+(?P<wavelength>.+)\.", re.MULTILINE | re.IGNORECASE)

    rx_iface_split = re.compile(r"Interface brief:\n", re.IGNORECASE)

    def execute(self):
        r = {"type": "CHASSIS",
             "number": "1",
             "vendor": "QTECH",
             }
        v = self.scripts.get_version()
        if "platform" not in v:
            return []
        r.update({
            "part_no": [v["platform"]],
            "revision": v["attributes"]["HW version"],
            "serial": v["attributes"]["Serial Number"]
        })
        r = [r]

        v = self.cli("show interface")
        for iface in self.rx_iface_split.split(v):
            if not iface:
                continue
            num = iface.split()[0].split("/")[-1]
            for t in self.rx_trans.finditer(iface):
                description = ""
                mfg_date = datetime.datetime.strptime(t.group("mfg_date"), "%b %d %Y")
                part_no = self.profile.convert_sfp(t.group("sfp_type"),
                                                   t.group("link_length"),
                                                   t.group("bit_rate"),
                                                   t.group("wavelength"))
                r += [{
                    "type": "XCVR",
                    "numper": num,
                    "vendor": t.group("vendor").strip(),
                    "part_no": part_no,
                    "serial": t.group("serial_number").strip(),
                    "mfg_date": mfg_date.strftime("%Y-%m-%d"),
                    "description": ""
                }]
        return r
