# ---------------------------------------------------------------------
# Huawei.VRP.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# Third-party modules
from collections import namedtuple
from dateutil.parser import parse as parse_date

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Huawei.VRP.get_inventory"
    interface = IGetInventory

    rx_hw = re.compile(
        r"DEVICE_NAME\s+:\s+(?P<part_no>\S+)\s*\n"
        r"DEVICE_SERIAL_NUMBER\s+:\s+(?P<serial>\S+)\s*\n"
        r"MAC_ADDRESS\s+:\s+(?P<mac>\S+)\s*\n"
        r"MANUFACTURING_DATE\s+:\s+(?P<mdate>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_header_start = re.compile(r"^\s*[-=]+\s*[-=]+", re.MULTILINE)
    rx_header_repl = re.compile(r"((Slot|Brd|Subslot|Sft|Unit|SubCard)\s)")

    rx_int_elabel_universal = re.compile(
        r"(?:\[(?P<sec_name>(?P<role>Rack|Back[Pp]lane|FanFrame|Slot|Main_Board|"
        r"Daughter_Board|[Pp]ort|PowerSlot|FanSlot|SubRack|[AB]\d|FAN\d|PWR\d)(?:_(?P<num>\S+)|))\]\n|)?\n?"
        r"(?:\/\$\[.+\]\s*\n"
        r"+\/\$(?:\S+=.*)\n+)+"
        r"(?P<properties>\[Board.?Properties\]\n(?:(?:\S+\=.*|[\w\s*,\(\)\*\/\-]+)\n)+)?",
        re.MULTILINE,
    )
    inventory_item = namedtuple(
        "InvItem", ["name", "num", "parent", "description", "type", "vendor", "barcode", "mnf_date"]
    )

    inv_property_map = {
        "boardtype": "type",
        "barcode": "barcode",
        "description": "description",
        "/edescription": "description",
        "manufactured": "mnf_date",
        "vendorname": "vendor",
        "/$vendorname": "vendor",
    }

    def parse_elabel(self, out):
        """
        Function parse 'display elabel'
        :param out: 'display elabel output'
        :type out: str
        :return:
        :rtype: inventory_item
        """
        r = []
        parent = None
        for match in self.rx_int_elabel_universal.finditer(out):
            match = match.groupdict()
            if not match:
                continue
            if match["role"] in {"Slot", "Rack"}:
                parent = match["sec_name"]
            if not match["properties"]:
                self.logger.debug(
                    "[%s] Empty [Board Properties] section. Skipping...", match["sec_name"]
                )
                continue
            p = parse_kv(self.inv_property_map, match["properties"], sep="=")
            if "vendor" not in p and "type" not in p:
                raise self.UnexpectedResultError("Partial parsed properties")
            if "vendor" not in p and p["type"].startswith("H"):
                p["vendor"] = "Huawei"
            elif "vendor" not in p or not p["vendor"]:
                self.logger.debug("[%s] Empty Vendor Properties. Skipping...", match["sec_name"])
                continue
            try:
                num = int(match["num"] or 0)
            except ValueError:
                num = match["num"]
            r += [
                self.inventory_item(
                    **{
                        "name": match["sec_name"],
                        "num": num,
                        "parent": parent,
                        "description": p.get("description"),
                        "type": p.get("type"),
                        "vendor": p.get("vendor", "Unknown"),
                        "barcode": p.get("barcode"),
                        "mnf_date": p.get("mnf_date"),
                    }
                )
            ]
        return r

    def part_parse_s8500(self):
        """
        Parse S85XX inventory
        :param items:
        :param slot_num:
        :return:
        """
        self.logger.info("Use S85XX parse function")
        slot_num, slots = self.get_device_inventory()
        r = [
            {
                "type": "CHASSIS",
                "number": 0,
                "vendor": "Huawei",
                "description": "",
                "part_no": [{14: "S8512", 10: "S8508", 7: "S8505", 4: "S8502"}[slot_num]],
            }
        ]
        for slot in slots:
            slot_n, subslot_n, part_no = slot["slot"], 0, slot["part_no"]
            # @todo CHASSIS !
            #  Slot No.   Brd Type        Brd Status   Subslot Num    Sft Ver
            # @todo  6         LSB1XP4CA0      Normal       1              S8500-VRP310-R1648P02
            # https://www.manualslib.com/manual/1216852/Huawei-Quidway-S8500-Series.html?page=52
            item_type, slot_n, part_no = self.get_type(slot_n, sub=subslot_n, part_no=part_no)
            v = self.cli("display device manuinfo slot %d" % slot["slot"])
            r += [
                {
                    "type": item_type,
                    "number": slot_n,
                    "vendor": "Huawei",
                    "description": "",
                    "part_no": [part_no],
                }
            ]
            r[-1].update(
                parse_kv(
                    {
                        "board_serial_number": "serial",
                        "device_serial_number": "serial",
                        "manufacturing_date": "mfg_date",
                        "vendor_name": "vendor",
                    },
                    v,
                )
            )
        return r

    cx_600_t = {"IPU", "LPU", "MPU", "SFU", "CLK", "PWR", "FAN", "POWER"}

    sfp_number = re.compile(r"^(?:Port_|port_|)(?P<type>\w+)\d+\/\d+\/(?P<num>\d+)")

    def get_type(self, slot, sub=None, name=None, part_no=None, descr="", slot_hints=None):
        """
        Resolve inventory type
        :param slot:
        :param sub:
        :param name:
        :param part_no:
        :param descr:
        :param slot_hints:
        :return: type, number, part_no
        :rtype: list
        """
        self.logger.debug(
            "Getting type. Slot: %s, Sub: %s, name: %s, part_no: %s, hints: %s",
            slot,
            sub,
            name,
            part_no,
            slot_hints,
        )
        if part_no.startswith("LSB"):
            # Huawei S8500
            self.logger.debug("IS Huawei S8500 linecard")
            return "LSB", slot, part_no
        if name and name.lower().startswith("port"):
            self.logger.debug("Detect type by by name")
            num = name
            if self.is_cloud_engine_switch:
                # On S5332 Cloud Engine port numbering in Type:
                # Port_GigabitEthernet0/0/4, Port_XGigabitEthernet0/0/4, Port_40GE0/0/4
                pass
            elif self.is_cloud_engine and self.sfp_number.match(name):
                # Port_10GE1/0/48, Port_10GE2/0/48
                num = "%s%s" % self.sfp_number.match(name).groups()
            elif self.sfp_number.match(name):
                # Port_GigabitEthernet2/0/19 format
                num = self.sfp_number.match(name).group("num")
            elif "_" in name:
                num = name.split("_")[-1]
            return "XCVR", num, part_no
        self.logger.debug("Detect type by by part_number")
        if part_no == "LE0MFSUA":
            return "CARD", slot, part_no
        if part_no.startswith("LE0"):
            return "LPU", slot, part_no
        if part_no.startswith("SAE"):
            return "LPU", slot, part_no
        if "CMU" in part_no:
            return "CMU", slot, part_no
        if "SRU" in part_no or "MPU" in part_no:
            return "SRU", slot, part_no
        if part_no.startswith("AR"):
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
        if self.is_cloud_engine and part_no.startswith("CE"):
            return "CHASSIS", slot, part_no
        if (
            not name
            and slot_hints
            and (
                part_no.endswith("PWD")
                or part_no.endswith("PWA")
                or part_no in ["PDC-350WC-B"]
                or self.is_cloud_engine_switch  # PDC1000S12-DB
            )
        ):
            # 5XX chassis PWR card
            # Try detect slot number by display device, use for 53XX series
            card = [x for x in slot_hints["subcards"] if x["type"] == "PWR" or x["type"] == part_no]
            num = card[0]["slot"]
            slot_hints["subcards"].remove(card[0])
            return "PWR", num, part_no
        if "PAC" in part_no:
            # PAC-350WB-L
            if name and self.rx_slot_num.match(name):
                # PWR1, PWR2
                slot = self.rx_slot_num.match(name).group("num")
            return "PWR", slot, part_no
        if part_no and part_no.startswith("FAN"):
            if name and self.rx_slot_num.match(name):
                # FAN1, FAN2
                slot = self.rx_slot_num.match(name).group("num")
            return "FAN", slot, part_no
        if not name and part_no.endswith("FANA"):
            # 5XXX FAN card
            return "FAN", 3, part_no
        # elif not sub and "FAN" in part_no:
        #    return "FAN", slot, None
        if not name and "stack interface card" in descr:
            # On S5320-36C-EI-28S-AC: LS5D21X02S01,LS5D21X02T01,LS5D21VST000 cards
            return "CARD", 1, part_no
        if not name and part_no.endswith("TPC"):
            # Slot 2 - TPC
            return "CARD", 2, part_no
        if not sub and "PWR" in part_no:
            return "PWR", slot, None
        if (not name or name == "Main_Board") and "Chassis" in descr:
            # 5XXX Series Cards
            # self.logger.debug("Huawei 5XXX series, slot 0 is CHASSIS TYPE")
            #
            return "CHASSIS", slot, part_no
        if "Physical Interface Card" in descr:
            return "PIC", slot, part_no
        if not name and "Card" in descr:
            # 5XXX Series Cards
            # self.logger.debug("Huawei 5XXX series, slot 0 is CHASSIS TYPE")
            # Slot 1 - Interface card
            #
            if slot == 0 and slot_hints:
                card = [x for x in slot_hints["subcards"] if x["type"] == part_no]
                if card:
                    slot = card[0]["slot"]
            return "CARD", slot, part_no
        if "Assembly Chassis" in descr:
            return "CHASSIS", slot, part_no
        if "Main Processing Unit" in descr:
            return "MPU", slot, part_no
        if "Interface Card" in descr:
            return "PIC", slot, part_no
        if "Network Processing Unit" in descr:
            return "NPU", slot, part_no
        if "Line Processing Unit" in descr:
            return "LPU", slot, part_no
        if "Switch and Route Processing Unit" in descr:
            return "SRU", slot, part_no
        if "Switch Fabric Unit" in descr:
            return "SFU", slot, part_no
        if "Flexible Card" in descr:
            return "FPIC", slot, part_no
        if "Fixed Card" in descr:
            return "FPIC", slot, part_no
        if "General Switch Control Unit" in descr:
            return "SCU", slot, part_no
        if "Fan Box" in descr or "Fan Module" in descr:
            if name and (name.startswith("A") or name.startswith("B")):
                slot = name
            return "FAN", slot, part_no
        if "Power Supply Unit" in descr or "Power Module" in descr or "Power Entry Module" in descr:
            if name and (name.startswith("A") or name.startswith("B")):
                slot = name
            elif name and self.rx_slot_num.match(name):
                # PWR1, PWR2
                slot = self.rx_slot_num.match(name).group("num")
            return "PWR", slot, part_no
        self.logger.info("Not response number place")
        return None, None, None

    rx_slot_num = re.compile(r"^(?P<type>\w+)(?P<num>\d+)")

    def get_device_inventory(self):
        """
        Get inventory table from "display device" command.
         Detect Slot and Subcard number and inventory type
        :rtype: List(Dict)
        """
        inv = []
        unit = False
        v = self.cli("display device")
        if "Unit " in v:
            unit = True
        slot_num = 0
        slot = 0
        for i in self.parse_table(v):
            i_slot, i_sub = None, None
            if "BrdType" in i:
                i_type = i["BrdType"]
            else:
                i_type = i.get("Type")
            if i_type == "NONE":
                # S85XX type
                slot_num += 1
                continue
            # Detect slot number
            if "Slot" in i:
                i_slot = i["Slot"]
            elif "Slot#" in i:
                i_slot = i["Slot#"]
            elif "Unit#" in i:
                i_slot = i["Unit#"]
            elif "SlotNo." in i:
                i_slot = i["SlotNo."]
            elif "SlotNo" in i:
                i_slot = i["SlotNo"]
            elif "Slot #" in i:
                i_slot = i["Slot #"]
            if i_slot and self.rx_slot_num.match(i_slot):
                # For FAN1, PWR2
                i_type, i_slot = self.rx_slot_num.match(i_slot).groups()
            try:
                slot = int(i_slot)
                slot_num += 1
            except ValueError:
                self.logger.warning("Slot have unknown text format...")
            except TypeError:
                self.logger.warning("Unknown 'display device' format..")
            if i_type == "POWER":
                i_type = "PWR"
            # Detect sub slot number
            if "Sub" in i:
                i_sub = i["Sub"]
            elif "SubCard#" in i:
                i_sub = i["SubCard#"]
            elif "SubCard #" in i:
                i_sub = i["SubCard #"]
            elif "SubslotNum" in i:
                i_sub = i["SubslotNum"]
            elif "SubSNo" in i:
                i_sub = i["SubSNo"]
            if i_sub == "-":
                i_sub = None
            if i_sub and self.rx_slot_num.match(i_sub):
                # For FAN1, PWR2
                i_type, i_sub = self.rx_slot_num.match(i_sub).groups()
            if i_sub:
                try:
                    i_sub = int(i_sub)
                except ValueError:
                    self.logger.warning("Sub have unknown text format...")
            if not i_sub or not inv or self.is_s85xx:
                # not inv for S85XX models
                inv += [
                    {"type": i_type, "slot": slot, "part_no": i_type, "unit": unit, "subcards": []}
                ]
            else:
                inv[-1]["subcards"] += [
                    {"type": i_type, "slot": i_sub, "part_no": i_type, "unit": unit}
                ]
        return slot_num, inv

    def parse_table(self, s):
        """List of Dict [{column1: row1, column2: row2}, ...]"""
        header_first_line = False

        if not self.rx_header_start.search(s):
            # if not header splitter in table
            header_first_line = True
        r = []
        columns = []
        l_old = ""
        chassis = ""
        s = s.splitlines()

        if "'" in s[0]:
            # Chassis: S5328C-EI-24S's Device status: that device table model - 5328C-24S
            ch = s.pop(0)
            chassis = ch.split("'")[0]
            r.append({"Slot": 0, "Sub": "-", "Type": ch.split("'")[0]})
        elif "Unit" in s[0]:
            # @todo Unit devices
            s.pop(0)
        for ll in s:
            if not ll.strip():
                continue
            if header_first_line:
                # If S85XX column with spaces:
                # Slot No.   Brd Type        Brd Status   Subslot Num    Sft Ver
                # Merge word
                ll = self.rx_header_repl.sub(r"\g<2>", ll)
                columns = [c.strip() for c in ll.split(" ") if c]
                header_first_line = False
                continue
            if self.rx_header_start.match(ll):
                if " #" in l_old:
                    # If Slot # in first column name - strip whitespace
                    l_old = self.rx_header_repl.sub(r"\g<2>", l_old)
                if columns:
                    # If header ----- \n header \n ------- format (C65xx)
                    r.pop()
                columns = l_old.split()
            elif columns:
                # Fetch cells
                row = ll.strip().split()
                if len(ll.strip().split()) != len(columns):
                    # First column is empty
                    row.insert(0, "-")
                # else:
                #    chassis = True
                if chassis and (chassis.startswith(row[2]) or r[-1]["Slot"] == 0):
                    # CHASSIS Already append, skipping
                    # r[-1]["Type"] = "CHASSIS"
                    chassis = ""
                    continue
                r.append(dict(zip(columns, row)))
                # r.append([l[f:t].strip() for f,t in columns])
            l_old = ll
        return r

    def to_keep_cli_session(self):
        if self.is_s77xx or self.is_s127xx:
            return False
        return self.keep_cli_session

    def execute_cli(self, **kwargs):
        r = []
        proccessed_serials = set()
        if self.is_s85xx:
            return self.part_parse_s8500()
        slot_num, device_slots = self.get_device_inventory()
        self.logger.debug("'display device' slots hints: %s", device_slots)
        cmd = "display elabel"
        if self.is_cloud_engine:
            cmd = "display device elabel"
        try:
            v = self.cli(cmd)
            parse_result = self.parse_elabel(v)
        except self.CLISyntaxError:
            r = self.scripts.get_version()
            inv = {
                "type": "CHASSIS",
                "number": 0,
                "vendor": "Huawei",
                "description": "",
                "part_no": r["platform"],
            }
            serial = self.capabilities.get("Chassis | Serial Number")
            if serial:
                inv["serial"] = serial
            revision = self.capabilities.get("Chassis | HW Version")
            if revision:
                inv["revision"] = revision
            return [inv]
            # raise NotImplementedError("Not supported 'display elabel' command")
        if self.is_cx300:
            # Chassis without SN ex. CX300
            r += [
                {
                    "type": "CHASSIS",
                    "number": 0,
                    "vendor": "Huawei",
                    "description": "",
                    "part_no": self.version["platform"],
                }
            ]
        parent_num = None
        for item in parse_result:
            self.logger.debug("Inventory item: %s", item)
            num = item.num
            if item.parent:
                parent_num = int(item.parent.split("_")[-1])
            if item.parent and (num == 0 or (item.name and item.name.startswith("Main_Board"))):
                num = parent_num
            if item.parent and len(device_slots) > parent_num:
                # Hack for S53XX, no number for PWR
                board_hints = device_slots[parent_num]
            else:
                board_hints = []
            i_type, slot_, _ = self.get_type(
                num,
                name=item.name,
                part_no=item.type,
                descr=item.description,
                slot_hints=board_hints,
            )
            if item.barcode in proccessed_serials and i_type != "XCVR":
                # CX600 has integrated card with same serial
                # but, Twinax will same S/N as normal
                continue
            if not i_type:
                i_type = "CHASSIS"
            proccessed_serials.add(item.barcode)  # Same serial on LPUI output
            data = {
                "type": i_type,
                "number": slot_,
                "vendor": item.vendor,
                "part_no": item.type,
                "serial": item.barcode,
                "description": item.description,
            }
            if item.description and "Fixed Card" in item.description:
                data["builtin"] = True
            if item.mnf_date:
                try:
                    mfg_date = parse_date(item.mnf_date)
                    if mfg_date.year > 1980:
                        # Check for "201�-��-�6" -> datetime.datetime(201, 6, 13, 0, 0)
                        data["mfg_date"] = mfg_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
            r += [data]
        return r
