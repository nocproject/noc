# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Raisecom.ROS.get_inventory"
    interface = IGetInventory

    rx_iface = re.compile(r"^(?P<ifname>\S+)\s+(?:UP|DOWN)\s+(?:UP|DOWN)", re.MULTILINE)
    rx_ifunit = re.compile(r"(?P<iftype>\D+)(?P<ifunit>\d+\S*)")
    rx_portnum = re.compile(r"^\S*?(?P<portnum>\d+)$")

    def execute_iscom2624g(self):
        v = self.scripts.get_version()
        r = [
            {
                "type": "CHASSIS",
                "vendor": "RAISECOM",
                "part_no": v["platform"],
                "revision": v["attributes"]["HW version"],
                "serial": v["attributes"]["Serial Number"],
            }
        ]
        v = self.cli("show interface brief")
        for match in self.rx_iface.finditer(v):
            ifname = self.profile.convert_interface_name(match.group("ifname"))
            match = self.rx_ifunit.search(ifname)
            iftype = match.group("iftype")
            if iftype not in ["fastethernet", "gigaethernet"]:
                continue
            ifunit = match.group("ifunit")
            port = self.cli(
                "show transceiver information %s %s " % (iftype, ifunit), ignore_errors=True
            )
            if port.strip() == "":
                continue
            match = self.rx_portnum.search(ifunit)
            num = match.group("portnum")
            xcvr = {"type": "XCVR", "number": num}
            for line in port.splitlines():
                try:
                    key, value = line.split(":")
                except ValueError:
                    continue
                if "Vendor Name" in key:
                    xcvr["vendor"] = value.strip()
                if "Vendor Part Number" in key:
                    xcvr["part_no"] = value.strip()
                if "Vendor Serial Number" in key:
                    xcvr["serial"] = value.strip()
                if "Vendor Version" in key:
                    xcvr["revision"] = value.strip()
            if "vendor" in xcvr:
                r += [xcvr]
        return r

    def execute_cli(self):
        if self.is_iscom2624g:
            return self.execute_iscom2624g()
        v = self.scripts.get_version()
        r = [
            {
                "type": "CHASSIS",
                "vendor": "RAISECOM",
                "part_no": v["platform"],
                "revision": v["attributes"]["HW version"],
                "serial": v["attributes"]["Serial Number"],
            }
        ]
        if self.is_rotek:
            return r
        v = self.cli("show interface port transceiver information")
        for port in v.split("Port "):
            if not port or "Wait" in port or "Error" in port:
                # Wait message after commands
                continue
            num = int(port.splitlines()[0].strip(":"))
            d = dict(e.split(":") for e in port.splitlines() if e and len(e.split(":")) == 2)
            # 1300Mb/sec-1310nm-LC-20.0km(0.009mm)
            description = "-".join(
                [
                    d["Transceiver Type"].strip(),
                    d["Wavelength(nm)"].strip() + "nm",
                    d["Connector Type"].strip(),
                    d["Transfer Distance(meter)"].strip() + "m",
                ]
            )
            if d["Vendor Part Number"].strip() == "Unknown":
                # Port 28:
                # Transceiver Type:
                # Connector Type:
                # Wavelength(nm): 2
                # Vendor Name: Unknown
                # Vendor Part Number: Unknown
                # Vendor Serial Number: Unknown
                # Fiber Type: Multi-Mode
                # Transfer Distance(meter): 2
                # SFP register information CRC recalculate ERROR!
                continue
            r += [
                {
                    "type": "XCVR",
                    "number": num,
                    "vendor": d["Vendor Name"].strip(),
                    "part_no": d["Vendor Part Number"].strip(),
                    "serial": d["Vendor Serial Number"].strip(),
                    "description": description,
                }
            ]
        return r
