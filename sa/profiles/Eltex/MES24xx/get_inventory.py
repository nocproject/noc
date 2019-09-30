# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES24xx.get_inventory
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
    name = "Eltex.MES24xx.get_inventory"
    interface = IGetInventory

    rx_trans = re.compile(
        r"^\s*Transceiver information:\s*\n"
        r"^\s*Vendor name: (?P<vendor>.+?)\s*\n"
        r"^\s*Serial number: (?P<serial>.+?)\s*\n"
        r"(^\s*Part number: (?P<part_no>.+?)\s*\n)?"
        r"(^\s*Vendor revision: (?P<revision>.+?)\s*\n)?"
        r"^\s*Connector type: (?P<conn_type>.+?)\s*\n"
        r"^\s*Transceiver type: (?P<type>.+?)\s*\n"
        r"^\s*Compliance code: (?P<code>.+?)\s*\n"
        r"^\s*Laser wavelength: (?P<wavelength>.+?)\s*\n"
        r"^\s*Transfer distance: (?P<distance>.+?)\s*\n",
        re.MULTILINE,
    )

    def get_trans(self, ifname):
        v = self.cli("show fiber-ports optical-transceiver detailed interface %s" % ifname)
        match = self.rx_trans.search(v)
        r = {"type": "XCVR", "vendor": match.group("vendor")}
        if match.group("serial"):
            r["serial"] = match.group("serial")
        if match.group("revision"):
            r["revision"] = match.group("revision")
        if ifname.startswith("gi"):
            r["number"] = "gi%s" % ifname.split("/")[-1]
        if ifname.startswith("te"):
            r["number"] = "te%s" % ifname.split("/")[-1]
        if match.group("part_no"):
            part_no = match.group("part_no")
        else:
            r["vendor"] = "OEM"
            code = match.group("code")
            if code == "1000BASE-LX":
                part_no = "NoName | Transceiver | 1G | SFP LX"
            elif code == "BaseBX10":
                wavelength = match.group("wavelength")
                if wavelength == "1310 nm":
                    part_no = "NoName | Transceiver | 1G | SFP BX10D"
                elif wavelength == "1490 nm":
                    part_no = "NoName | Transceiver | 1G | SFP BX10U"
                else:
                    # raise self.NotSupportedError()
                    part_no = "NoName | Transceiver | 1G | SFP"
            elif code == "10GBASE-LR":
                part_no = "NoName | Transceiver | 10G | SFP+ LR"
            elif code == "unknown":
                part_no = "NoName | Transceiver | 1G | SFP"
            else:
                raise self.NotSupportedError()
        r["part_no"] = part_no
        return r

    def execute_cli(self, **kwargs):
        v = self.scripts.get_version()
        res = [
            {
                "type": "CHASSIS",
                "vendor": "ELTEX",
                "part_no": v["platform"],
                "revision": v["attributes"]["HW version"],
                "serial": v["attributes"]["Serial Number"],
            }
        ]
        v = self.cli("show fiber-ports optical-transceiver")
        for i in parse_table(v):
            port = i[0]
            if port.startswith("Gi"):
                port_ifname = "gigabitethernet %s" % port[2:]
            elif port.startswith("Fa"):
                port_ifname = "fastethernet %s" % port[2:]
            c = self.cli("show fiber-ports optical-transceiver %s" % port_ifname)
            match = self.rx_trans.search(c)
            if match:
                r = {"type": "XCVR", "vendor": match.group("vendor")}
                if match.group("serial"):
                    r["serial"] = match.group("serial")
                if match.group("revision"):
                    r["revision"] = match.group("revision")
                    r["number"] = port.split("/")[-1]
                if match.group("part_no"):
                    part_no = match.group("part_no")
                else:
                    r["vendor"] = "OEM"
                    code = match.group("code")
                    if code == "1000BASE-LX":
                        part_no = "NoName | Transceiver | 1G | SFP LX"
                    elif code == "BaseBX10":
                        wavelength = match.group("wavelength")
                        if wavelength == "1310 nm":
                            part_no = "NoName | Transceiver | 1G | SFP BX10D"
                        elif wavelength == "1490 nm":
                            part_no = "NoName | Transceiver | 1G | SFP BX10U"
                        else:
                            # raise self.NotSupportedError()
                            part_no = "NoName | Transceiver | 1G | SFP"
                    elif code == "unknown":
                        part_no = "NoName | Transceiver | 1G | SFP"
                    else:
                        raise self.NotSupportedError()
                r["part_no"] = part_no
                res += [r]
        return res
