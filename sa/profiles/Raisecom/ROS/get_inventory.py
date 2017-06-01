# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Raisecom.ROS.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.profile.get_version(self)
        r = [{
            "type": "CHASSIS",
            "number": "1",
            "vendor": "RAISECOM",
            "part_no": v["platform"],
            "revision": v["hw_rev"],
            "serial": v["serial"]
        }]
        v = self.cli("show interface port transceiver information")
        for port in v.split("Port "):
            if not port:
                continue
            num = int(port.splitlines()[0].strip(":"))
            d = dict([e.split(":") for e in port.splitlines() if e])
            # 1300Mb/sec-1310nm-LC-20.0km(0.009mm)
            description = "-".join([d["Transceiver Type"].strip(),
                                    d["Wavelength(nm)"].strip() + "nm",
                                    d["Connector Type"].strip(),
                                    d["Transfer Distance(meter)"].strip() + "m"
                                    ])
            r += [{
                "type": "XCVR",
                "numper": num,
                "vendor": d["Vendor Name"].strip(),
                "part_no": d["Vendor Part Number"].strip(),
                "serial": d["Vendor Serial Number"].strip(),
                "description": description
            }]
        return r
