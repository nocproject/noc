# -*- coding: utf-8 -*-
"""
__author__ = 'FeNikS'
##----------------------------------------------------------------------
## Huawei.VRP.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
# Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Huawei.VRP.get_inventory"
    interface = IGetInventory

    rx_slot_key = re.compile(
        r"^\d+|PWR\d+|FAN\d+|CMU\d", re.DOTALL | re.MULTILINE | re.VERBOSE)
    rx_backplane = re.compile(
        r"\[(?P<type>BackPlane)_(?P<number>.*?)\]"
        r"(?P<body>.*?)"
        r"(?P<bom>BOM=.*?)", re.DOTALL | re.MULTILINE | re.VERBOSE)
    rx_slot = re.compile(
        r"\[(?P<type>Slot)_(?P<number>.*?)\]"
        r"(?P<body>.*?)"
        r"(?P<bom>BOM=.*?)", re.DOTALL | re.MULTILINE | re.VERBOSE)
    rx_port = re.compile(
        r"\[Port_(?P<port_num>\d+)\].+?\n\n\[Board\sProperties\](?P<body>.*?)\n\n",
        re.DOTALL | re.MULTILINE | re.VERBOSE
    )
    rx_mainboard = re.compile(
        r"\[Main_Board\].+?\n\n\[Board\sProperties\](?P<body>.*?)\n\n",
        re.DOTALL | re.MULTILINE | re.VERBOSE
    )
    rx_subitem = re.compile(
        r"\[(?P<type>Port|Daughter_Board)_(?P<number>.*?)\]"
        r"(?P<body>.*?)"
        r"(?P<bom>BOM=.*?)", re.DOTALL | re.MULTILINE | re.VERBOSE)
    rx_item_content = re.compile(
        r"\[Board.Properties\]\n"
        r"Board Type=(?P<board_type>.*?)\n"
        r"BarCode=(?P<bar_code>.*?)\n"
        r"Item=(?P<item>.*?)\n"
        r"Description=(?P<desc>.*?)\n"
        r"Manufactured=(?P<mnf_date>.*?)\n"
        r"^.*?VendorName=(?P<vendor>.*?)\n"
        r"IssueNumber=(?P<issue_number>.*?)\n"
        r"CLEICode=(?P<code>.*?)\n", re.DOTALL | re.MULTILINE | re.VERBOSE | re.IGNORECASE)

    rx_item_content2 = re.compile(
        r"Board Type=(?P<board_type>.*?)\n"
        r"BarCode=(?P<bar_code>.*?)\n"
        r"Item=(?P<item>.*?)\n"
        r"Description=(?P<desc>.*?)\n"
        r"Manufactured=(?P<mnf_date>.*?)\n"
        r"^.*?VendorName=(?P<vendor>.*?)\n"
        r"IssueNumber=(?P<issue_number>.*?)\n"
        r"CLEICode=(?P<code>.*?)\n", re.DOTALL | re.MULTILINE | re.VERBOSE | re.IGNORECASE)

    def parse_item_content(self, item, number, item_type):
        """Parse display elabel block"""
        match_body = self.rx_item_content2.search(item)
        vendor = match_body.group("vendor").strip()
        serial = match_body.group("bar_code").strip()
        part_no = match_body.group("board_type")
        desc = match_body.group("desc")
        manufactured = match_body.group("mnf_date")
        if manufactured and part_no:
            manufactured = self.normalize_date(manufactured)
        if part_no == "":
            return None
        if vendor == "":
            vendor = "NONAME"

        return {
            "type": item_type,
            "number": number,
            "vendor": vendor.upper(),
            "serial": serial,
            "description": desc,
            "part_no": [part_no],
            "revision": None,
            "mfg_date": manufactured if manufactured else None
        }

    def part_parse(self, type, slot_num, subcard_num=""):
        v = self.cli("display elabel slot %s %s" % (slot_num or "", subcard_num))
        r = []

        if type == "CHASSIS":
            f = re.search(self.rx_mainboard, v)
            sh = self.parse_item_content(f.group("body"), slot_num, "CHASSIS")
            r.append(sh)
        elif type == "XCVR":
            for f in re.finditer(self.rx_port, v):
                num = f.group("port_num")
                sfp = self.parse_item_content(f.group("body"), num, "XCVR")
                if sfp:
                    r.append(sfp)
        else:
            r.append(self.parse_item_content(v, subcard_num, type))

        return r

    def get_inv(self):
        """Get inventory table"""
        inv = []
        v = self.cli("display device")
        s = self.parse_table(v)
        for i in s:
            type = i["Type"]
            if i["Slot"] == "0" and i["Sub"] == "-":
                num = i["Slot"]
                type = "CHASSIS"
            elif i["Slot"] == "-":
                num = i["Sub"]
            elif i["Slot"] != "-":
                num = i["Slot"]
            elif self.rx_slot_key.match(i["Slot"]):
                num = i["Slot"][3:]
                type = i["Slot"][0:3]
            else:
                self.logger("Not response number place")
                continue
            inv.append(
                {
                    "type": type,
                    "number": num,
                    "vendor": "HUAWEI"
                }
            )

        return inv

    @staticmethod
    def parse_table(s):
        """List of Dict [{column1: row1, column2: row2}, ...]"""
        rx_header_start = re.compile(r"^\s*[-=]+\s+[-=]+")

        r = []
        columns = []
        chassis = False
        for l in s.splitlines():
            if not l.strip():
                continue
            if rx_header_start.match(l):
                columns = l_old.split()
            elif columns:
                """Fetch cells"""
                row = l.strip().split()
                if len(l.strip().split()) != len(columns):
                    """First column is empty"""
                    row.insert(0, "-")
                    if chassis:
                        # @todo Make algoritm to response chassis
                        r[-1]["Type"] = "CHASSIS"
                        chassis = False
                else:
                    chassis = True
                r.append(dict(zip(columns, row)))
                # r.append([l[f:t].strip() for f,t in columns])
            l_old = l
        return r

    @staticmethod
    def normalize_date(date):
        """Normalize date in input to YYYY-MM-DD"""
        result = date
        need_edit = False
        parts = date.split('-')
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        if month < 10:
            month = '0' + str(month)
            need_edit = True
        if day < 10:
            day = '0' + str(day)
            need_edit = True
        if len(str(year)) < 4:
            year = "2" + "0" * (3-len(str(year))) + str(year)
            need_edit = True
        if need_edit:
            parts = [year, month, day]
            result = '-'.join([str(el) for el in parts])
        return result

    def execute(self):
        objects = []
        slot_num = 0

        items = self.get_inv()
        for i in items:
            if i["type"] == "CHASSIS":
                objects.extend(self.part_parse(i["type"], i["number"]))
                for si in self.part_parse("XCVR", i["number"]):
                    objects.append(si)
                slot_num = i["number"]
            else:
                objects.extend(self.part_parse(i["type"], slot_num, i["number"]))

        return objects
