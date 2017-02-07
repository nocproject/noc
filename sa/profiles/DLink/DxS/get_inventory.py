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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "DLink.DxS.get_inventory"
    interface = IGetInventory

    rx_dev = re.compile(
        r"Device Type\s+:\s*(?P<part_no>\S+).+"
        r"[Hh]ardware [Vv]ersion\s+:\s*(?P<revision>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_des = re.compile(r"Device Type\s+:\s*(?P<descr>.+?)\n")
    rx_ser = re.compile(
        r"(?:[Ss]erial [Nn]umber|Device S/N)\s+:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_stack = re.compile(
        r"^\s*(?P<box_id>\d+)\s+(?P<part_no>\S+)\s+(?P<revision>\S+)\s+"
        r"(?P<serial>\S*)", re.MULTILINE)
    rx_mod = re.compile(
        r"Module Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod1 = re.compile(
        r"Module 1 Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod2 = re.compile(
        r"Module 2 Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod3 = re.compile(
        r"\s+(?P<number>\d+)\s+(?P<part_no>\S+)\s+(?P<revision>\S+)\s+"
        r"(?P<serial>(\xFF)+)\s+(?P<descr>.+?)\s*$")
    rx_media_type = re.compile(
        r"^\s(?P<unit>\d+)?:?(?P<port>\d+)\s+(\(F\))?\s+(?:SFP LC|\-)\s+"
        r"(?P<vendor>.+?)/\s+(?P<part_no>.+?)/\s+(?P<serial>.+?)/\s+\n"
        r"\s+\S+\s*:\S+\s*:\S+\s+(?P<revision>\S+)?\s+\d+\s+\n"
        r"\s+Compatibility: Single Mode \(SM\),"
        r"(?P<mbd>\d+)Mbd, (?P<nm>\d+)nm\n", re.MULTILINE)
    fake_vendors = ["OEM", "CISCO-FINISAR"]

    def execute(self):
        r = []
        stacks = []
        s = self.scripts.get_switch()
        match = self.rx_dev.search(s)
        part_no = match.group("part_no")
        revision = match.group("revision")
        if part_no.startswith("DES-3200-") and revision != "A1":
            part_no = "%s/%s" % (part_no, revision)
        if (part_no.startswith("DES-1210-10/ME") or
            part_no.startswith("DES-1210-26/ME") or
            part_no.startswith("DES-1210-28/ME") and
            revision != "A1"):
            part_no = "%s/%s" % (part_no, revision)
        p = {
            "type": "CHASSIS",
            "vendor": "DLINK",
            "part_no": [part_no],
            "revision": revision
        }
        ser = self.rx_ser.search(s)
        if (ser and ser.group("serial") != "System" and
            ser.group("serial") != "Power"):
            p["serial"] = ser.group("serial")
        p["description"] = self.rx_des.search(s).group("descr")
        try:
            s = self.cli("show stack_device")
            for match in self.rx_stack.finditer(s):
                stacks += [match.groupdict()]
        except self.CLISyntaxError:
            pass
        r += [p]
        box_id = 1
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
        try:
            c = self.cli("show ports media_type")
            for match in self.rx_media_type.finditer(c):
                if match.group("unit") and match.group("unit") != box_id:
                    box_id = match.group("unit")
                    for i in stacks:
                        if i["box_id"] == box_id:
                            p = {
                                "type": "CHASSIS",
                                "vendor": "DLINK",
                                "part_no": [i["part_no"]],
                                "revision": i["revision"]
                            }
                            if i["serial"]:
                                p["serial"] = i["serial"]
                            r += [p]
                            break
                vendor = match.group("vendor")
                part_no = match.group("part_no")
                description = match.group("part_no")
                revision = match.group("revision")
                mbd = int(match.group("mbd"))
                nm = int(match.group("nm"))
                if vendor in self.fake_vendors:
                    vendor = "NONAME"
                    part_no = 'NoName | Transceiver | '
                    if mbd == 1300 and nm == 1310:
                        part_no = part_no + '1G | SFP BXU'
                    elif mbd == 1300 and nm == 1550:
                        part_no = part_no + '1G | SFP BXD'
                    elif mbd == 1200 and nm == 1310:
                        part_no = part_no + '1G | SFP BX10U'
                    elif mbd >= 1200 and nm == 1490:
                        part_no = part_no + '1G | SFP BX10D'
                    elif mbd >= 1000 and nm == 0:
                        if description.endswith(tuple([" EX", "-EX"])):
                            part_no = part_no + '1G | SFP EX'
                        elif description.endswith(tuple([" LH", "-LH"])):
                            part_no = part_no + '1G | SFP LH'
                        elif description.endswith(tuple([" LX", "-LX"])):
                            part_no = part_no + '1G | SFP LX'
                        elif description.endswith(tuple([" SX", "-SX"])):
                            part_no = part_no + '1G | SFP SX'
                        elif description.endswith(tuple([" T", "-T"])):
                            part_no = part_no + '1G | SFP T'
                        elif description.endswith(tuple([" TX", "-TX"])):
                            part_no = part_no + '1G | SFP TX'
                        elif description.endswith(tuple([" ZX", "-ZX"])):
                            part_no = part_no + '1G | SFP ZX'
                        else:
                            part_no = part_no + '1G | SFP'
                    elif mbd == 100 and nm == 1310:
                        part_no = part_no + '100M | SFP BX100U'
                    elif mbd == 100 and nm == 1550:
                        part_no = part_no + '100M | SFP BX100D'
                    else:
                        part_no = part_no + 'Unknown SFP'

                i = {
                    "type": "XCVR",
                    "number": match.group("port"),
                    "vendor": vendor,
                    "part_no": part_no,
                    "serial": match.group("serial"),
                    "description": "%s, %dMbd, %dnm" % (description, mbd, nm)
                }
                if revision is not None:
                    i["revision"] = revision
                r += [i]
        except self.CLISyntaxError:
            pass

        return r
