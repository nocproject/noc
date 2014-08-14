# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError

class Script(NOCScript):
    name = "DLink.DxS.get_inventory"
    implements = [IGetInventory]

    TIMEOUT = 300

    rx_dev = re.compile(
        r"Device Type\s+:\s+(?P<part_no>\S+).+"
        r"Hardware Version\s+:\s+(?P<revision>\S+)", re.MULTILINE | re.DOTALL)
    rx_des = re.compile(r"Device Type\s+:\s+(?P<descr>.+?)\n")
    rx_ser = re.compile(
        r"(?:Serial Number|Device S/N)\s+:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_mod = re.compile(r"Module Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod1 = re.compile(r"Module 1 Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod2 = re.compile(r"Module 2 Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod3 = re.compile(
        r"\s+(?P<number>\d+)\s+(?P<part_no>\S+)\s+(?P<revision>\S+)\s+"
        r"(?P<serial>(\xFF)+)\s+(?P<descr>.+?)\s*$")

    def execute(self):
        r = []
        s = self.cli("show switch", cached=True)
        match = self.rx_dev.search(s)
        part_no = match.group("part_no")
        revision = match.group("revision")
        if part_no.startswith("DES-3200-") and revision != "A1":
            part_no = "%s/%s" % (part_no, revision)
        if (part_no.startswith("DES-1210-10/ME/B") or
            part_no.startswith("DES-1210-26/ME/B") or
            part_no.startswith("DES-1210-28/ME/B")):
            part_no = "%s/%s" % (part_no, revision)
        p = {
            "type": "CHASSIS",
            "number": "1",
            "vendor": "DLINK",
            "part_no": [part_no],
            "revision": revision
        }
        ser = self.rx_ser.search(s)
        if (ser and ser.group("serial") != "System" and
            ser.group("serial") != "Power"):
            p["serial"] = ser.group("serial")
        p["description"] = self.rx_des.search(s).group("descr")
        r += [p]
        match = self.rx_mod.search(s)
        if match:
            p = {
                "type": "MODULE",
                "vendor": "DLINK",
                "part_no": [match.group("part_no")],
            }
            if match.group("descr"):
                p["description"] = match.group("descr")
            r += [p]
        match = self.rx_mod1.search(s)
        if match and match.group("part_no") != "None":
            p = {
                "type": "MODULE",
                "number": "1",
                "vendor": "DLINK",
                "part_no": [match.group("part_no")],
            }
            if match.group("descr"):
                p["description"] = match.group("descr")
                r += [p]
        match = self.rx_mod2.search(s)
        if match and match.group("part_no") != "None":
            p = {
                "type": "MODULE",
                "number": "2",
                "vendor": "DLINK",
                "part_no": [match.group("part_no")],
            }
            if match.group("descr"):
                p["description"] = match.group("descr")
                r += [p]
        try:
            s = self.cli("show module_info")
            for l in s.splitlines():
                match = self.rx_mod3.search(l)
                if match and match.group("part_no") != "-":
                    p = {
                        "type": "MODULE",
                        "number": match.group("number"),
                        "vendor": "DLINK",
                        "part_no": [match.group("part_no")],
                        "description": [match.group("descr")],
                    }
                    r += [p]
        except self.CLISyntaxError:
            pass

        return r
