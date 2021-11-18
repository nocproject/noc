# ----------------------------------------------------------------------
# NSN.TIMOS.get_inventory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "NSN.TIMOS.get_inventory"
    interface = IGetInventory

    rx_iom = re.compile(
        r"^(?P<number>\d+)\s+(?P<name>iom\S+)\s+(?:up|down)\s+(?:up|down)\s+"
        r"\d+\s+(?P<comments>\S+)?"
    )
    rx_imm = re.compile(r"^(?P<number>\d+)\s+(?P<name>imm\d*\S+)\s+(?:up|down)\s+(?:up|down)")
    rx_mda = re.compile(
        r"^(?P<slot>\d+)/(?P<number>\d+)\s+(?P<name>(?:m|imm)\d+\S+)\s+(?:up|down)\s+(?:up|down)"
    )
    rx_sfm = re.compile(r"^(?P<number>A|B)\s+(?P<name>sfm\d*\S+)\s+(?:up|down)\s+(?:up|down)")
    rx_cpm = re.compile(r"^(?P<number>A|B)\s+(?P<name>cpm\d+)\s+(?:up|down)\s+(?:up|down)")
    rx_ch = re.compile(
        r"^\s*Hardware Data\s*\n"
        r"^\s+Part number\s+:\s+(?P<part_no>\S+)\s*\n"
        r"^\s+CLEI code\s+:\s+(?P<clei>\S+)\s*\n"
        r"^\s+Serial number\s+:\s+(?P<serial>\S+)\s*\n"
        r"^\s+Manufacture date\s+:\s+(?P<mfg_date>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_descr = re.compile(r"^\s+Type\s+:\s+(?P<type>.+)\s*\n", re.MULTILINE)
    rx_hw = re.compile(
        r"^Hardware Data\s*\n"
        r"^\s+Platform type\s+:\s+(?P<platform>\S+)\s*\n"
        r"^\s+Part number\s+:\s+(?P<part_no>\S+)\s*\n"
        r"^\s+CLEI code\s+:\s+(?P<clei>\S+)\s*\n"
        r"^\s+Serial number\s+:\s+(?P<serial>\S+)\s*\n"
        r"^\s+Manufacture date\s+:\s+(?P<mfg_date>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_flash = re.compile(
        r"^Flash\s+\-\s+cf(?P<number>\d+):\s*\n"
        r"^\s+Administrative State\s+:\s+up\s*\n"
        r"^\s+Operational state\s+:\s+up\s*\n"
        r"^\s+Serial number\s+:\s+(?P<serial>\S+)\s*\n"
        r"^\s+Firmware revision\s+:\s+(?P<revision>\S+)\s*\n"
        r"^\s+Model number\s+:\s+(?P<part_no>.+)\s*\n",
        re.MULTILINE,
    )
    rx_date = re.compile(r"(?P<m>\d{2})(?P<d>\d{2})(?P<y>\d{4})")

    CHASSIS_TYPES = {
        1: "other",
        2: "unknown",
        3: "CHASSIS",
        4: "container",
        5: "PSU",
        6: "FAN",
        7: "sensor",
        8: "IOM",
        9: "CPM",
        10: "CFM",
        11: "MDA",
        12: "flashDiskModule",
        13: "port",
        14: "mcm",
        15: "CCM",
        16: "oesCard",
        17: "oesControlCard",
        18: "oesUserPanel",
        19: "alarmInputModule",
        20: "pcm",
    }

    def get_date(self, d):
        match = self.rx_date.search(d)
        m = match.group("m")
        d = match.group("d")
        y = match.group("y")
        return "-".join([y, m, d])

    def execute_snmp(self):
        r = []
        try:
            for v in self.snmp.get_tables(
                [
                    "1.3.6.1.4.1.6527.3.1.2.2.1.8.1.4",  # part_no
                    "1.3.6.1.4.1.6527.3.1.2.2.1.8.1.5",  # serial
                    "1.3.6.1.4.1.6527.3.1.2.2.1.8.1.6",  # date
                    "1.3.6.1.4.1.6527.3.1.2.2.1.8.1.7",  # type
                    "1.3.6.1.4.1.6527.3.1.2.2.1.8.1.8",  # alias
                ],
                max_retries=1,
            ):
                if v[1] and (v[4] == 3 or v[4] == 8):
                    types = self.CHASSIS_TYPES[v[4]]
                    p = {
                        "type": types,
                        "vendor": "NSN",
                        "part_no": [v[1]],
                        "serial": v[2],
                    }
                    if type != "CHASSIS":
                        num = v[5]
                        p["number"] = num[-1]
                    if v[3].isdigit():
                        p["mfg_date"] = self.get_date(v[3])
                    r += [p]
        except self.snmp.TimeOutError:
            pass
        return r

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show chassis detail ")
        except self.CLISyntaxError:
            v = self.cli("show chassis")
        match = self.rx_ch.search(v)
        p = {
            "type": "CHASSIS",
            "vendor": "NSN",
            "part_no": [match.group("part_no")],
            "serial": match.group("serial"),
            "mfg_date": self.get_date(match.group("mfg_date")),
        }
        match = self.rx_descr.search(v)
        p["description"] = match.group("type").strip()
        r += [p]
        v = self.cli("show card state")
        for ll in v.split("\n"):
            p = {}
            match = self.rx_iom.search(ll)
            if match:
                number = match.group("number")
                p = {
                    "type": "IOM",
                    "number": number,
                    "vendor": "NSN",
                    "part_no": [match.group("name")],
                    "description": match.group("comments"),
                }
                c = self.cli("show card %s detail" % number)
                match1 = self.rx_hw.search(c)
                if match1:
                    p["part_no"] = [match1.group("part_no")]
                    p["serial"] = match1.group("serial")
                    p["mfg_date"] = self.get_date(match1.group("mfg_date"))
                r += [p]
            match = self.rx_imm.search(ll)
            if match:
                number = match.group("number")
                p = {
                    "type": "IMM",
                    "number": number,
                    "vendor": "NSN",
                    "part_no": [match.group("name")],
                }
                c = self.cli("show card %s detail" % number)
                match1 = self.rx_hw.search(c)
                if match1:
                    p["part_no"] = [match1.group("part_no")]
                    p["serial"] = match1.group("serial")
                    p["mfg_date"] = self.get_date(match1.group("mfg_date"))
                    p["description"] = match1.group("platform")
                r += [p]
            match = self.rx_mda.search(ll)
            if match:
                number = match.group("number")
                p = {
                    "type": "MDA",
                    "number": number,
                    "vendor": "NSN",
                    "part_no": [match.group("name")],
                }
                c = self.cli("show mda %s/%s detail" % (match.group("slot"), number))
                match1 = self.rx_hw.search(c)
                if match1:
                    p["part_no"] = [match1.group("part_no")]
                    p["serial"] = match1.group("serial")
                    p["mfg_date"] = self.get_date(match1.group("mfg_date"))
                    p["description"] = match1.group("platform")
                r += [p]
            match = self.rx_sfm.search(ll)
            if match:
                number = match.group("number")
                p = {
                    "type": "SFM",
                    "number": number,
                    "vendor": "NSN",
                    "part_no": [match.group("name")],
                }
                c = self.cli("show card %s detail" % number)
                match1 = self.rx_hw.search(c)
                if match1:
                    p["part_no"] = [match1.group("part_no")]
                    p["serial"] = match1.group("serial")
                    p["mfg_date"] = self.get_date(match1.group("mfg_date"))
                    p["description"] = match1.group("platform")
                r += [p]
                for match1 in self.rx_flash.finditer(c):
                    if "NSN" in match1.group("part_no"):
                        vendor = "NSN"
                    else:
                        vendor = "NONAME"
                    p = {
                        "type": "CF",
                        "number": match1.group("number"),
                        "vendor": vendor,
                        "part_no": [match1.group("part_no").strip()],
                        "serial": match1.group("serial"),
                        "revision": match1.group("revision"),
                    }
                    r += [p]
            match = self.rx_cpm.search(ll)
            if match:
                number = match.group("number")
                p = {
                    "type": "CPM",
                    "number": number,
                    "vendor": "NSN",
                    "part_no": [match.group("name")],
                }
                c = self.cli("show card %s detail" % number)
                match1 = self.rx_hw.search(c)
                if match1:
                    p["part_no"] = [match1.group("part_no")]
                    p["serial"] = match1.group("serial")
                    p["mfg_date"] = self.get_date(match1.group("mfg_date"))
                    p["description"] = match1.group("platform")
                r += [p]
                for match1 in self.rx_flash.finditer(c):
                    if "NSN" in match1.group("part_no"):
                        vendor = "NSN"
                    else:
                        vendor = "NONAME"
                    p = {
                        "type": "CF",
                        "number": match1.group("number"),
                        "vendor": vendor,
                        "part_no": [match1.group("part_no").strip()],
                        "serial": match1.group("serial"),
                        "revision": match1.group("revision"),
                    }
                    r += [p]
        return r
