# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_inventory
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
        r"\[(?:Main_Board|BackPlane_0)\].+?\n\n\[Board\sProperties\](?P<body>.*?)\n\n",
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
        r"Board(\s|)Type=(?P<board_type>.*?)(\n|)"
        r"BarCode=(?P<bar_code>.*?)(\n|)"
        r"\s*Item=(?P<item>.*?)\n"
        r"Description=(?P<desc>.*?)\n"
        r"Manufactured=(?P<mnf_date>.*?)(\n|)"
        r".*?VendorName=(?P<vendor>.*?)(\n|)"
        r"IssueNumber=(?P<issue_number>.*?)\n"
        r"CLEICode=(?P<code>.*?)\n", re.DOTALL | re.MULTILINE | re.VERBOSE | re.IGNORECASE)

    rx_hw = re.compile(
        r"DEVICE_NAME\s+:\s+(?P<part_no>\S+)\s*\n"
        r"DEVICE_SERIAL_NUMBER\s+:\s+(?P<serial>\S+)\s*\n"
        r"MAC_ADDRESS\s+:\s+(?P<mac>\S+)\s*\n"
        r"MANUFACTURING_DATE\s+:\s+(?P<mdate>\S+)\s*\n", re.MULTILINE)

    unit = False

    def parse_item_content(self, item, number, item_type):
        """Parse display elabel block"""
        date_check = re.compile("\d+-\d+-\d+")
        match_body = self.rx_item_content2.search(item)
        if not match_body or match_body is None:
            self.logger.info("Port number %s not having asset" % number)
        vendor = match_body.group("vendor").strip()
        serial = match_body.group("bar_code").strip()
        part_no = match_body.group("board_type").strip()
        desc = match_body.group("desc")
        manufactured = match_body.group("mnf_date")
        if vendor == "":
            vendor = "NONAME"
        if " " in serial:
            serial = serial.split()[0]
        if manufactured and part_no and date_check.match(manufactured):
            manufactured = self.normalize_date(manufactured)
        else:
            manufactured = None

        return {
            "type": item_type,
            "number": number,
            "vendor": vendor.upper(),
            "serial": serial,
            "description": desc,
            "part_no": [part_no],
            "revision": None,
            "mfg_date": manufactured
        }

    def part_parse(self, i_type, slot_num, subcard_num=""):
        """
        Getting detail information about slot from display elabel command
        :param i_type: Inventory type
        :param slot_num: Number slot, installed card
        :param subcard_num: Number subcard on slot, empty if device not support subcard
        """
        v_cli = "display elabel slot %s %s"
        if self.unit:
            v_cli = "display elabel unit %s %s"
        elif self.match_version(platform__regex="^(S93..|AR[12].+)$"):
            v_cli = "display elabel %s %s"
        try:
            v = self.cli(v_cli % (slot_num, subcard_num))
        except self.CLISyntaxError:
            return []
        # Avoid of rotten devices, where part_on contains 0xFF characters
        v = v.decode("ascii", "ignore")
        r = []

        if i_type == "CHASSIS":
            f = re.search(self.rx_mainboard, v)
            sh = self.parse_item_content(f.group("body"), slot_num, "CHASSIS")
            r.append(sh)
        else:
            r.append(self.parse_item_content(v, subcard_num, i_type))

        for f in re.finditer(self.rx_port, v):
            # port block, search XCVR
            num = f.group("port_num")
            if f.group("body") == '':
                self.logger.info("Slot %s, Port %s not having asset" % (slot_num, num))
                continue
            sfp = self.parse_item_content(f.group("body"), num, "XCVR")
            if not sfp.get("part_no", [])[0] and not sfp.get("serial"):
                # Skipping SFP
                self.logger.debug("Not p_no in SFP slot, %s skipping" % num)
                continue
            if sfp:
                r.append(sfp)

        return r

    def get_inv(self):
        """
        Get inventory table. Detect Slot and Subcard number and inventory type
        """
        # @todo Stack
        inv = []
        v = self.cli("display device")
        if "Unit " in v:
            self.unit = True
        slot_num = 0
        s = self.parse_table(v)
        chassis = False
        for i in s:
            i_type = i["Type"]
            # Detect slot number
            if "Slot" in i:
                i_slot = i["Slot"]
            elif "Unit#" in i:
                i_slot = i["Unit#"]
            else:
                i_slot = 0

            # Detect sub slot number
            if "Sub" in i:
                i_sub = i["Sub"]
            elif "SubCard#" in i:
                i_sub = i["SubCard#"]
            else:
                i_sub = None
            if i_sub == "-":
                i_sub = ""
            i_type, number, part_no = self.get_type(i_slot, i_sub, i_type)

            if i_slot != "-":
                self.logger.info("Slot Number constant")
                slot_num = number
            self.logger.debug("%s, %s ,%s", i_type, number, part_no)
            if i_type == "CHASSIS" and not chassis:
                inv.extend(self.part_parse(i_type, number))
                chassis = True
            elif i_type == "CHASSIS" and chassis:
                # chassis must be only one
                self.logger.info("chassis must be only one, Skipping...")
                continue
            else:
                inv.extend(self.part_parse(i_type, slot_num, i_sub))
            """
            inv += [{
                "type": type,
                "number": number,
                "part_no": part_no,
                "vendor": "HUAWEI"
            }]
            """

        return inv

    @staticmethod
    def parse_table(s):
        """List of Dict [{column1: row1, column2: row2}, ...]"""
        rx_header_start = re.compile(r"^\s*[-=]+\s*[-=]+", re.MULTILINE)
        rx_header_repl = re.compile(r"((Slot|Brd|Subslot|Sft|Unit|SubCard)\s)")
        header_first_line = False

        if not rx_header_start.search(s):
            # if not header splitter in table
            header_first_line = True

        r = []
        columns = []
        l_old = ""
        chassis = ""
        s = s.splitlines()

        if "'" in s[0]:
            # Chassis: S5328C-EI-24S's Device status:
            ch = s.pop(0)
            chassis = ch.split("'")[0]
            r.append({"Type": "CHASSIS",
                      "Slot": 0,
                      "Sub": "-",
                      "part_no": ch.split("'")[0]})
        elif "Unit" in s[0]:
            # @todo Unit devices
            s.pop(0)

        for l in s:
            if not l.strip():
                continue
            if header_first_line:
                """
                If S85XX column with spaces:
                Slot No.   Brd Type        Brd Status   Subslot Num    Sft Ver
                Merge word
                """
                l = rx_header_repl.sub(r"\g<2>", l)
                columns = [c.strip() for c in l.split(" ") if c]
                header_first_line = False
                continue
            if rx_header_start.match(l):
                if " #" in l_old:
                    # If Slot # in first column name - strip whitespace
                    l_old = rx_header_repl.sub(r"\g<2>", l_old)
                columns = l_old.split()
            elif columns:
                """Fetch cells"""
                row = l.strip().split()
                if len(l.strip().split()) != len(columns):
                    """First column is empty"""
                    row.insert(0, "-")
                # else:
                #    chassis = True
                if chassis and chassis == row[2]:
                    # CHASSIS Already append, skipping
                    # @todo Make algoritm to response chassis
                    # r[-1]["Type"] = "CHASSIS"
                    chassis = ""
                    continue

                r.append(dict(zip(columns, row)))
                # r.append([l[f:t].strip() for f,t in columns])
            l_old = l
        return r

    @staticmethod
    def normalize_date(date):
        """Normalize date in input to YYYY-MM-DD"""
        d = re.compile("\d+")
        result = date
        need_edit = False
        parts = date.split('-')
        year = int(parts[0])
        month = int(parts[1])
        day = int(d.search(parts[2]).group(0))
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

    def get_type(self, slot, sub, part_no):
        """
        Resolve inventory type
        :param slot:
        :param sub:
        :param part_no:
        :return: type, number, part_no
        :rtype: list
        """
        cx_600_t = ["LPU", "MPU", "SFU", "CLK", "PWR", "FAN", "POWER"]
        self.logger.info("Getting type %s, %s, %s", slot, sub, part_no)

        try:
            slot = int(slot)
        except ValueError:
            if "PWR" in str(slot) or "FAN" in str(slot):
                return slot[0:3], slot[3], None
            self.logger.warning("Slot have unknown text format...")
            return None, None, None

        if sub:
            try:
                sub = int(sub)
            except ValueError:
                self.logger.warning("Sub have unknown text format...")

        if slot == 0 and not sub:
            return "CHASSIS", 0, part_no
        elif slot == 0 and sub == 0:
            return "CHASSIS", 0, part_no
        elif sub and part_no in cx_600_t:
            return part_no, sub, None
        elif slot and part_no in cx_600_t:
            return part_no, slot, None
        elif not sub and part_no in cx_600_t:
            return part_no, slot, None
        elif part_no.startswith("LE0"):
            return "FRU", slot, part_no
        elif part_no.startswith("AR"):
            # AR Series ISR, Examples:
            # "SIC": ["AR0MSEG1CA00"], "WSIC": ["AR01WSX220A"], "XSIC": ["AR01XSX550A"], "SRU": ["AR01SRU2C"],
            # PWR: ["AR01PSAC35"]
            if "SRU" in part_no:
                tp = "SRU"
            elif part_no[4] == "S" or part_no[-1] == "S":
                tp = "SIC"
            elif part_no[4:6] == "WS":
                tp = "WSIC"
            elif part_no[4:6] == "XS":
                tp = "XSIC"
            elif part_no[4:6] == "PS":
                tp = "PWR"
            else:
                return None, slot, part_no
            return tp, slot, part_no
        elif "PAC" in part_no:
            # PAC-350WB-L
            return "PWR", slot, part_no
        elif not sub and "FAN" in part_no:
            return "FAN", slot, None
        elif not sub and "PWR" in part_no:
            return "PWR", slot, None

        else:
            self.logger.info("Not response number place")
            return None, None, None

    def execute(self):
        items = self.get_inv()
        if not items:
            try:
                match = self.rx_hw.search(self.cli("display device manuinfo"))
            except self.CLISyntaxError:
                return []
            if match:
                return [{
                    "type": "CHASSIS",
                    "vendor": "HUAWEI",
                    "serial": match.group("serial"),
                    "part_no": [match.group("part_no")],
                    "revision": None,
                    "mfg_date": match.group("mdate")
                }]

        return items
