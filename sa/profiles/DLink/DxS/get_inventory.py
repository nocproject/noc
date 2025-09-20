# ---------------------------------------------------------------------
# DLink.DxS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import datetime

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "DLink.DxS.get_inventory"
    interface = IGetInventory

    rx_dev = re.compile(
        r"Device Type\s+:\s*(?P<part_no>\S+).+[Hh]ardware [Vv]ersion\s+:\s*(?P<revision>\S+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_des = re.compile(r"Device Type\s+:\s*(?P<descr>.+?)\n")
    rx_ser = re.compile(
        r"(?:[Ss]erial [Nn]umber|Device S/N)\s+:\s*(?P<serial>\S+)\s*\n", re.MULTILINE | re.DOTALL
    )
    rx_stack = re.compile(
        r"^\s*(?P<box_id>\d+)\s+(?P<part_no>\S+)\s+(?P<revision>\S+)\s+(?P<serial>\S*)",
        re.MULTILINE,
    )
    rx_mod = re.compile(r"Module Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod1 = re.compile(r"Module 1 Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod2 = re.compile(r"Module 2 Type\s+: (?P<part_no>\S+)\s*(?P<descr>.*?)\n")
    rx_mod3 = re.compile(
        r"\s+(?P<number>\d+)\s+(?P<part_no>\S+)\s+(?P<revision>\S+)\s+"
        r"(?P<serial>(\xFF)+)\s+(?P<descr>.+?)\s*$"
    )
    rx_media_type = re.compile(
        r"^\s((?P<unit>\d+):)?(?P<port>\d+)\s+(\(F\))?\s+(?:SFP LC|\-)\s+"
        r"(?P<vendor>.+?)/\s+(?P<part_no>.+?)/\s+(?P<serial>.+?)/\s*\n"
        r"\s+\S+\s*:\S+\s*:\S+\s+(?P<revision>\S+)?\s+(?P<mfg_date>\d+)\s*\n"
        r"\s+Compatibility: Single Mode \(SM\),"
        r"(?P<mbd>\d+)Mbd, (?P<nm>\d+)nm\n",
        re.MULTILINE,
    )
    rx_media_type1210 = re.compile(
        r"^(?P<port>\d+)\s+\(F\)\s+SFP \- (?:LC|SC|Copper pigtail)\s*"
        r"(?P<vendor>\S+)\s+(?P<part_no>\S+)\s+(?P<serial>\S+)\s*\n"
        r"\s+\S+\s*:\S+\s*:\S+\s+(?P<revision>\S*)?\s+(?P<mfg_date>\d+)\s*\n"
        r"\s+Compatibility:\s+(?:Single Mode|Unallocated|),\s+"
        r"(?P<mbd>\d+)\s*Mbd,\s+(?P<nm>\d+)\s*nm\n",
        re.MULTILINE,
    )
    rx_mfg_date = re.compile(r"^(?P<year>\d+\d+)(?P<month>\d\d)(?P<day>\d\d)")
    fake_vendors = ["OEM", "CISCO-FINISAR"]

    @classmethod
    def build_xcvr(cls, match):
        vendor = match.group("vendor")
        part_no = match.group("part_no")
        description = match.group("part_no")
        revision = match.group("revision")
        mfg_date = match.group("mfg_date")
        mbd = int(match.group("mbd"))
        nm = int(match.group("nm"))
        if vendor in cls.fake_vendors:
            vendor = "NONAME"
            part_no = "NoName | Transceiver | "
            if mbd == 1300 and nm == 1310:
                part_no = part_no + "1G | SFP BXU"
            elif mbd == 1300 and nm == 1550:
                part_no = part_no + "1G | SFP BXD"
            elif mbd == 1200 and nm == 1310:
                part_no = part_no + "1G | SFP BX10U"
            elif mbd >= 1200 and nm == 1490:
                part_no = part_no + "1G | SFP BX10D"
            elif mbd >= 1000 and nm == 0:
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
                else:
                    part_no = part_no + "1G | SFP"
            elif mbd == 100 and nm == 1310:
                part_no = part_no + "100M | SFP BX100U"
            elif mbd == 100 and nm == 1550:
                part_no = part_no + "100M | SFP BX100D"
            else:
                part_no = part_no + "Unknown SFP"
        i = {
            "type": "XCVR",
            "number": match.group("port"),
            "vendor": vendor,
            "part_no": part_no,
            "serial": match.group("serial"),
            "description": "%s, %dMbd, %dnm" % (description, mbd, nm),
        }
        if revision is not None:
            i["revision"] = revision
        match = cls.rx_mfg_date.search(mfg_date)
        if match:
            d = "20%s-%s-%s" % (match.group("year"), match.group("month"), match.group("day"))
            try:
                valid_date = datetime.date.fromisoformat(d)
                if valid_date < datetime.date.today():
                    i["mfg_date"] = d
            except ValueError:
                pass
        return i

    def execute_cli(self, **kwargs):
        r = []
        stacks = []
        s = self.scripts.get_switch()
        v = self.scripts.get_version()
        part_no = v["platform"]
        p = {"type": "CHASSIS", "vendor": "DLINK", "part_no": [part_no]}
        if "Chassis | HW Version" in v["caps"]:
            p["revision"] = v["caps"]["Chassis | HW Version"]
        if "Chassis | Serial Number" in v["caps"]:
            p["serial"] = v["caps"]["Chassis | Serial Number"]
        match = self.rx_des.search(s)
        if match:
            p["description"] = match.group("descr")
        if self.is_stack:
            s = self.cli("show stack_device")
            for match in self.rx_stack.finditer(s):
                stacks += [match.groupdict()]
        if not stacks:
            r += [p]
        box_id = "0"
        match = self.rx_mod.search(s)
        if match:
            p = {"type": "MODULE", "vendor": "DLINK", "part_no": [match.group("part_no")]}
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
            for line in s.splitlines():
                match = self.rx_mod3.search(line)
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
            found = False
            for match in self.rx_media_type.finditer(c):
                if match.group("unit") and match.group("unit") != box_id:
                    box_id = match.group("unit")
                    for i in stacks:
                        if i["box_id"] == box_id:
                            p = {
                                "type": "CHASSIS",
                                "number": i["box_id"],
                                "vendor": "DLINK",
                                "part_no": [i["part_no"]],
                                "revision": i["revision"],
                            }
                            if i["serial"]:
                                p["serial"] = i["serial"]
                            r += [p]
                            break
                i = self.build_xcvr(match)
                r += [i]
                found = True
            if not found:  # Try to parse other exotic hardware output
                for match in self.rx_media_type1210.finditer(c):
                    i = self.build_xcvr(match)
                    r += [i]

        except self.CLISyntaxError:
            pass

        return r
