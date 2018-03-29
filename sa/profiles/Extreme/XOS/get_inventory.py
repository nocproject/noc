# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
import datetime
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.text import parse_kv
from noc.lib.validators import is_int


class Script(BaseScript):
    name = "Extreme.XOS.get_inventory"
    interface = IGetInventory

    rx_trans_split = re.compile(r"Port\s+(\S+)\n")
    rx_no_trans = re.compile(r"No ([\S\+\/]+) detected\.")

    rx_power_split = re.compile(r"PowerSupply\s+(\d+)\s+information:")

    rx_fans_split = re.compile(r"(Slot-\d+|)\s*FanTray(-\d+|)\s+information:")

    def get_transiever(self, slot=None):
        r = []
        k_map = {"sfp/sfp+ vendor": "vendor",
                 "vendor": "vendor",
                 "sfp/sfp+ part number": "part_no",
                 "partnumber": "part_no",
                 "sfp/sfp+ serial number": "serial",
                 "serialnumber": "serial",
                 "manufacturedate": "mfg_date",
                 "sfp/sfp+ manufacture date": "mfg_date",
                 "connector": "connector",
                 "type": "type",
                 "wavelength": "wavelength",
                 "sfp or sfp+": "sfp_type",
                 "rev": "rev"}
        if slot:
            v = "debug hal show optic-info slot %d" % slot
        else:
            v = "debug hal show optic-info"
        v = self.cli(v)
        port = None
        for block in self.rx_trans_split.split(v):
            if is_int(block):
                port = block.strip()
                continue
            if self.rx_no_trans.match(block) or not port:
                continue
            d = parse_kv(k_map, block)
            # 1300Mb/sec-1310nm-LC-20.0km(0.009mm)
            # description = ""
            description = "-".join([d.get("type", "").strip(),
                                    d.get("wavelength", "").strip() + "nm",
                                    d.get("connector", "").strip()
                                    # d["Transfer Distance(meter)"].strip() + "m"
                                    ])
            if "part_no" not in d:
                continue
            if "mfg_date" in d:
                try:
                    if len(d["mfg_date"]) > 6:
                        d["mfg_date"] = d["mfg_date"][:6]
                    d["mfg_date"] = datetime.datetime.strptime(d["mfg_date"], "%y%m%d")
                    d["mfg_date"] = d["mfg_date"].strftime("%Y-%m-%d")
                except ValueError:
                    self.logger.error("Unconverted format manufactured date: %s, on port: %s" % (d["mfg_date"], port))
                    d["mfg_date"] = None
            r += [{
                "type": "XCVR",
                "number": port,
                "vendor": d.get("vendor", "NONAME"),
                "part_no": d["part_no"].strip(),
                "serial": d.get("serial", ""),
                "description": description,
                "mfg_date": d.get("mfg_date", "00-00-00")
            }]
            if "rev" in d:
                r[-1]["revision"] = d["rev"]
            port = None
        return r

    def get_psu(self):
        r = defaultdict(list)
        k_map = {"state": "state",
                 "partinfo": "partinfo"}
        try:
            v = self.cli("show power detail")
        except self.CLISyntaxError:
            return {}
        slot = 1
        number = None
        for block in self.rx_power_split.split(v):
            if is_int(block):
                if int(block.strip()) < number:
                    slot += 1
                number = int(block.strip())
                continue
            d = parse_kv(k_map, block)
            if d.get("state") in ["Empty", "Powered Off", None] or "partinfo" not in d:
                continue
            partinfo = d["partinfo"].split()

            r[slot] += [{
                "type": "PSU",
                "number": number,
                "description": "".join(partinfo[:-2]),
                "vendor": "EXTREME",
                "part_no": partinfo[-1],
                "serial": partinfo[-2]
            }]
        return r

    def get_fan(self):
        r = defaultdict(list)
        k_map = {"state": "state",
                 "numfan": "numfan",
                 "partinfo": "partinfo",
                 "revision": "rev"}
        try:
            v = self.cli("show fans detail")
        except self.CLISyntaxError:
            return {}
        slot = 1
        for block in self.rx_fans_split.split(v):
            if "Slot-" in block:
                slot = int(block.split("-")[1].strip())
                continue
            d = parse_kv(k_map, block)
            if d.get("state") in ["Empty", None] or "partinfo" not in d:
                continue
            serial_no, part_no = d["partinfo"].split()
            r[slot] += [{
                "type": "FAN",
                "number": 1,
                "description": "FanTray",
                "vendor": "EXTREME",
                "part_no": part_no,
                "revision": d["rev"],
                "serial": serial_no
            }]
        return r

    def get_slot(self):
        r = {}
        try:
            v = self.cli("show slot")
        except self.CLISyntaxError:
            return r
        for line in v.splitlines()[2:]:
            if not line.startswith("Slot-"):
                continue
            line = line.split()
            if "Empty" in line:
                continue
            slot = line[0].strip()
            r[slot] = {"type": line[1].strip(),
                       "configured": line[2].strip(),
                       "state": line[3].strip()}
        return r

    def get_type(self, m_type):
        r = "CHASSIS"
        if "PSU" in m_type:
            return "PSU"
        return r

    def execute_cli(self):
        r = []
        v = self.cli("show version", cached=True)
        slots = self.get_slot()
        psu = self.get_psu()
        fan = self.get_fan()
        for line in v.splitlines():
            if not line or ":" not in line:
                continue
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if "Switch" in k:
                k = "Switch-1"
            elif "PSU" in k:
                continue
            elif "-" not in k or not v:
                continue
            ss = slots.get(k)
            m_type, m_number = k.split("-")
            slot = int(m_number)
            m_part_no, serial_no, rev = v.split(" ", 2)
            rev = rev.split(" ")[1]
            r += [{
                "type": self.get_type(m_type),
                "number": m_number,
                "description": ss["type"] if ss else "",
                "vendor": "EXTREME",
                "part_no": m_part_no,
                "revision": rev,
                "serial": serial_no
            }]
            if slot in psu:
                r += psu[slot]
            if slot in fan:
                r += fan[slot]
            r += self.get_transiever(slot=slot if ss else None)
        return r
