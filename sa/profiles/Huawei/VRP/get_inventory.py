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

    @staticmethod
    def parse_item_content(rx_match, number, type, prefix_number=''):
        rx_item_content = re.compile(
            r"Board Type=(?P<board_type>.*?)\n"
            r"BarCode=(?P<bar_code>.*?)\n"
            r"Item=(?P<item>.*?)\n"
            r"Description=(?P<desc>.*?)\n"
            r"Manufactured=(?P<mnf_date>.*?)\n"
            r"^.*?VendorName=(?P<vendor>.*?)\n"
            r"IssueNumber=(?P<issue_number>.*?)\n"
            r"CLEICode=(?P<code>.*?)\n", re.DOTALL | re.MULTILINE | re.VERBOSE | re.IGNORECASE)

        # type = rx_match.group("type")
        # number = rx_match.group("number")
        match_body = rx_item_content.search(rx_match)
        # board_type = match_body.group("board_type")

        # if board_type:
        #     if type == "Daughter_Board":
        #         number = ''.join([prefix_number, '/', number])
        #     elif type == "Port":
        #         number = ''.join([prefix_number, '/0/', number])

            # type = ' '.join([type, board_type])
        vendor = match_body.group("vendor").strip()
        serial = match_body.group("bar_code").strip()
        part_no = match_body.group("board_type")
        desc = match_body.group("desc")
        # manufactured = match_body.group("mnf_date")
        # if manufactured:
        #     manufactured = self.normalize_date(manufactured)
        if part_no == "":
            return None
        return {
            "type": type,
            "number": number,
            "vendor": vendor.upper(),
            "serial": serial,
            "description": desc,
            "part_no": [part_no]
            # "mfg_date": manufactured if manufactured else None}]
        }

        # return None

    def sfp_parse(self, type, slot_num, subcard_num=""):
        v = self.cli("display elabel slot %s %s" % (slot_num or "", subcard_num))
        r = []

        if type == "CHASSIS":
            f = re.search(self.rx_mainboard, v)
            sh = self.parse_item_content(f.group("body"), slot_num, "CHASSIS")
            # sh["number"] = None
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
        inv = []
        stack = True
        v = self.cli("display device")
        s = self.parse_table(v)
        for i in s:
            if i["Type"] == "-":
                continue
            if i["Slot"] != "-":
                num = i["Slot"]
            elif i["Slot"] == "-":
                num = i["Sub"]
            else:
                continue
            if i["Sub"] == "-":
                type = "CHASSIS"
            else:
                type = i["Type"]
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
        rx_header_start = re.compile(r"^\s*[-=]+\s+[-=]+")
        rx_col = re.compile(r"^(\s*)([\-]+|[=]+)")

        columns = None
        r = []
        r2 = []
        columns = []
        for l in s.splitlines():
            if not l.strip():
                # columns = []
                continue

            if rx_header_start.match(l): # Column delimiters found. try to determine column's width
                columns = l_old.split()

            elif columns: # Fetch cells
                row = l.strip().split()
                r.append(row)
                if len(l.strip().split()) != len(columns):
                    row.insert(0, "-")
                r2.append(dict(zip(columns, row)))
                #r.append([l[f:t].strip() for f,t in columns])
            l_old = l
        return r2

    @staticmethod
    def normalize_date(date):
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
                objects.extend(self.sfp_parse(i["type"], i["number"]))
                for si in self.sfp_parse("XCVR", i["number"]):
                    objects.append(si)
                slot_num = i["number"]
            else:
                objects.extend(self.sfp_parse(i["type"], slot_num, i["number"]))
        # items2 = self.sfp_parse(0)
        """
        try:
            cmd_result = self.cli("display elabel")
        except self.CLISyntaxError:
           raise self.NotSupportedError()


        backplane_regexp = self.rx_backplane.search(cmd_result)
        if backplane_regexp:
           objects += self.parse_item_content(backplane_regexp)

        # parse slots using device table
        cmd_result = self.cli("display device")
        for item in self.rx_slot_key.finditer(cmd_result):
            cmd_result = self.cli("display elabel 1/%s" % (item.group(0)))
            slot_regexp = self.rx_slot.search(cmd_result)
            if slot_regexp:
                add_item = self.parse_item_content(slot_regexp)
                if add_item:
                    objects += add_item

                slot_number = slot_regexp.group("number")
                for subitem in self.rx_subitem.finditer(cmd_result):
                    add_item = self.parse_item_content(subitem, slot_number)
                    if add_item:
                        objects += add_item
        """

        return objects
