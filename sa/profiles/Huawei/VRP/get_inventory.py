# -*- coding: utf-8 -*-
__author__ = 'FeNikS'
##----------------------------------------------------------------------
## Huawei.VRP.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory

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

def parse_item_content(rx_match, prefix_number=''):
    type = rx_match.group("type")
    number = rx_match.group("number")
    match_body = rx_item_content.search(rx_match.group("body"))
    board_type = match_body.group("board_type")

    if board_type:
        if type == "Daughter_Board":
            number = ''.join([prefix_number, '/', number])
        elif type == "Port":
            number = ''.join([prefix_number, '/0/', number])

        type = ' '.join([type, board_type])
        vendor = match_body.group("vendor").strip()
        serial = match_body.group("bar_code")
        part_no = match_body.group("item")
        desc = match_body.group("desc")
        manufactured = match_body.group("mnf_date")
        if manufactured:
            manufactured = normalize_date(manufactured)

        return [{
            "type": type,
            "number": number,
            "vendor": vendor,
            "serial": serial,
            "description": desc,
            "part_no": [part_no],
            "mfg_date": manufactured if manufactured else None}]

    return None

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

class Script(NOCScript):
    name = "Huawei.VRP.get_inventory"
    implements = [IGetInventory]

    def execute(self):
        objects = []
        cmd_result = self.cli("display elabel")

        backplane_regexp = rx_backplane.search(cmd_result)
        if backplane_regexp:
            objects += parse_item_content(backplane_regexp)

        #parse slots using device table
        cmd_result = self.cli("display device")
        for item in rx_slot_key.finditer(cmd_result):
            cmd_result = self.cli("display elabel 1/%s" % (item.group(0)))
            slot_regexp = rx_slot.search(cmd_result)
            if slot_regexp:
                add_item = parse_item_content(slot_regexp)
                if add_item:
                    objects += add_item

                slot_number = slot_regexp.group("number")
                for subitem in rx_subitem.finditer(cmd_result):
                    add_item = parse_item_content(subitem, slot_number)
                    if add_item:
                        objects += add_item

        return objects