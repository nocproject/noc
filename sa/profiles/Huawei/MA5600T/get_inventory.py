# ---------------------------------------------------------------------
# Huawei.MA5600T.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import namedtuple, defaultdict

# Third party modules
from dateutil.parser import parse

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_kv
from noc.core.mib import mib


class Script(BaseScript):
    name = "Huawei.MA5600T.get_inventory"
    interface = IGetInventory
    always_prefer = "C"

    SNMP_UNKNOWN_VALUE = 2147483647
    SNMP_INVALID_VALUE = -1

    MEASURE_TYPES = {
        "C": "Celsius",
        "%R.H.": "Percent",
        "V": "Volt DC",
        "A": "Ampere",
    }

    rx_slot = re.compile(
        r"^\s*Pcb\s+Version\s*:\s+(?P<part_no>\S+)\s+VER (?P<revision>\S+)\s*\n",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_sub = re.compile(
        r"^\s*(VOIP)?SubBoard(\[(?P<number>\d+)\])?:\s*\n"
        r"^\s*Pcb\s+Version\s*:\s+(?P<part_no>\S+)\s+"
        r"VER (?P<revision>\S+)\s*\n",
        re.MULTILINE | re.IGNORECASE,
    )

    rx_inv_item_split = re.compile(
        r"\[(?P<role>Back[Pp]lane|FanFrame|Slot|Main_Board|Daughter_Board)(?:_(?P<num>\d+)|)\]\n"
        r"\/\$\[(?:Archi(?:e|)ve(?:r|)s\s*Info|Board\s*Integration)\s*Version\]\n"
        r"\/\$(?:Archi(?:e|)ve(?:r|)s\s*Info|Board\s*Integration)\s*Version=3\.0\n+",
        re.MULTILINE,
    )

    rx_inv_port_split = re.compile(
        r"\[[Pp]ort_(?P<name>\S+)\]\n"
        r"\/\$\[(?:Archi(?:e|)ve(?:r|)s\s*Info|Board\s*Integration)\s*Version\]\n"
        r"\/\$(?:Archi(?:e|)ve(?:r|)s\s*Info|Board\s*Integration)\s*Version=3\.0\n+",
        re.MULTILINE,
    )

    rx_int_elabel = re.compile(
        r"\[(?P<sec_name>"
        r"(?P<role>Rack|Back[Pp]lane|FanFrame|Slot|Main_Board|Daughter_Board|[Pp]ort)(?:_(?P<num>\S+)|))\]\n"
        r"\/\$\[(?:Archi(?:e|)ve(?:r|)s\s*Info|Board\s*Integration)\s*Version\]\n"
        r"\/\$(?:Archi(?:e|)ve(?:r|)s\s*Info|Board\s*Integration)\s*Version=3\.0\n+"
        r"(?P<properties>\[Board Properties\]\n(?:(?:\S+\=.*|[\w\s*,\(\)\*\/\-]+)\n)+)?",
        re.MULTILINE,
    )

    rx_int_elabel_universal = re.compile(
        r"\[(?P<sec_name>"
        r"(?P<role>Rack|Back[Pp]lane|FanFrame|Slot|Main_Board|Daughter_Board|[Pp]ort)(?:_(?P<num>\S+)|))\]\n"
        r"(?:\/\$\[.+\]\n"
        r"+\/\$(?:\S+=.*)\n+)+"
        r"(?P<properties>\[Board Properties\]\n(?:(?:\S+\=.*|[\w\s*,\(\)\*\/\-]+)\n)+)?",
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
    }

    def get_chassis_sensors(self):
        if not self.has_snmp():
            return []
        r = []
        # hwAnaChannelTable
        for oid, v in self.snmp.getnext(mib["HUAWEI-ENVIRONMENT-MIB::hwAnaName"], bulk=False):
            _, key = oid.rsplit(".", 1)
            measure = self.snmp.get(mib["HUAWEI-ENVIRONMENT-MIB::hwAnaMeasureType", key])
            value = self.snmp.get(mib["HUAWEI-ENVIRONMENT-MIB::hwAnaCurrentValue", key])
            if value and value != self.SNMP_UNKNOWN_VALUE and measure:
                r += [
                    {
                        "name": v,
                        "status": True,
                        "description": v,
                        "measurement": self.MEASURE_TYPES[measure],
                        "snmp_oid": mib["HUAWEI-ENVIRONMENT-MIB::hwAnaCurrentValue", key],
                    }
                ]
        # hwDigChannelTable
        for oid, v in self.snmp.getnext(
            mib["HUAWEI-ENVIRONMENT-MIB::hwDigChannelName"], bulk=False
        ):
            _, key1, key2 = oid.rsplit(".", 2)
            v = v.lower()
            if "door" in v or "heater" in v:
                value = self.snmp.get(mib["HUAWEI-ENVIRONMENT-MIB::hwDigChannelState", key1, key2])
                if value and value != self.SNMP_INVALID_VALUE:
                    r += [
                        {
                            "name": v,
                            "status": True,
                            "description": v,
                            "measurement": "Scalar",
                            "snmp_oid": mib[
                                "HUAWEI-ENVIRONMENT-MIB::hwDigChannelState", key1, key2
                            ],
                        }
                    ]
        # hwFanTable
        for oid, v in self.snmp.getnext(mib["HUAWEI-ENVIRONMENT-MIB::hwFanName"], bulk=False):
            _, key = oid.rsplit(".", 1)
            value = self.snmp.get(mib["HUAWEI-ENVIRONMENT-MIB::hwCurrentTemp", key])
            if value and value != self.SNMP_UNKNOWN_VALUE:
                r += [
                    {
                        "name": "fan_temp",
                        "status": True,
                        "description": "Температура в блоке вентиляторов",
                        "measurement": "Celsius",
                        "snmp_oid": mib["HUAWEI-ENVIRONMENT-MIB::hwCurrentTemp", key],
                    }
                ]
            value = self.snmp.get(mib["HUAWEI-ENVIRONMENT-MIB::hwFanSpeed", key])
            if value and value != self.SNMP_INVALID_VALUE:
                r += [
                    {
                        "name": "fan_speed",
                        "status": True,
                        "description": "Скорость вращения вентиляторов",
                        "measurement": "Percent",
                        "snmp_oid": mib["HUAWEI-ENVIRONMENT-MIB::hwFanSpeed", key],
                    }
                ]
        # hwACInputEntry
        for oid, v in self.snmp.getnext(mib["HUAWEI-POWER-MIB::hwACPowerState"], bulk=False):
            _, key = oid.rsplit(".", 1)
            if v:
                r += [
                    {
                        "name": "ac_state",
                        "status": True,
                        "description": "Наличие напряжения AC",
                        "measurement": "Scalar",
                        "snmp_oid": mib["HUAWEI-POWER-MIB::hwACPowerState", key],
                    }
                ]
            value = self.snmp.get(mib["HUAWEI-POWER-MIB::hwACVoltA", key])
            if value and value != self.SNMP_INVALID_VALUE:
                r += [
                    {
                        "name": "ac_volt",
                        "status": True,
                        "description": "Напряжение AC",
                        "measurement": "Volt AC",
                        "snmp_oid": mib["HUAWEI-POWER-MIB::hwACVoltA", key],
                    }
                ]
        # hwDCOutEntry
        for oid, v in self.snmp.getnext(mib["HUAWEI-POWER-MIB::hwDCVoltageOut"], bulk=False):
            _, key = oid.rsplit(".", 1)
            if v:
                r += [
                    {
                        "name": "dc_volt",
                        "status": True,
                        "description": "Напряжение DC",
                        "measurement": "Volt DC",
                        "snmp_oid": mib["HUAWEI-POWER-MIB::hwDCVoltageOut", key],
                    }
                ]
            value = self.snmp.get(mib["HUAWEI-POWER-MIB::hwDCCurrentOut", key])
            if value and value != self.SNMP_INVALID_VALUE:
                r += [
                    {
                        "name": "dc_current",
                        "status": True,
                        "description": "Ток DC",
                        "measurement": "Ampere",
                        "snmp_oid": mib["HUAWEI-POWER-MIB::hwDCCurrentOut", key],
                    }
                ]
            value = self.snmp.get(mib["HUAWEI-POWER-MIB::hwDCVoltageOutState", key])
            if value:
                r += [
                    {
                        "name": "dc_state",
                        "status": True,
                        "description": "Наличие напряжения DC",
                        "measurement": "Scalar",
                        "snmp_oid": mib["HUAWEI-POWER-MIB::hwDCVoltageOutState", key],
                    }
                ]
        # hwBatteryTable
        for oid, v in self.snmp.getnext(mib["HUAWEI-POWER-MIB::hwBatteryCapacity"], bulk=False):
            _, key = oid.rsplit(".", 1)
            if v <= 0:
                continue
            volt = self.snmp.get(mib["HUAWEI-POWER-MIB::hwBatteryVoltage", key])
            current = self.snmp.get(mib["HUAWEI-POWER-MIB::hwBatteryCurrent", key])
            temp = self.snmp.get(mib["HUAWEI-POWER-MIB::hwBatteryTemperature", key])
            if temp != self.SNMP_UNKNOWN_VALUE and volt != self.SNMP_INVALID_VALUE:
                r += [
                    {
                        "name": "battery_volt",
                        "status": True,
                        "description": "Напряжение АКБ",
                        "measurement": "Volt DC",
                        "snmp_oid": mib["HUAWEI-POWER-MIB::hwBatteryVoltage", key],
                    }
                ]
                if current != self.SNMP_INVALID_VALUE:
                    r += [
                        {
                            "name": "battery_current",
                            "status": True,
                            "description": "Ток АКБ",
                            "measurement": "Ampere",
                            "snmp_oid": mib["HUAWEI-POWER-MIB::hwBatteryCurrent", key],
                        }
                    ]
                r += [
                    {
                        "name": "battery_temp",
                        "status": True,
                        "description": "Температура АКБ",
                        "measurement": "Celsius",
                        "snmp_oid": mib["HUAWEI-POWER-MIB::hwBatteryTemperature", key],
                    },
                    {
                        "name": "battery_state",
                        "status": True,
                        "description": "Текущее состояние АКБ",
                        "measurement": "Scalar",
                        "snmp_oid": mib["HUAWEI-POWER-MIB::hwBatteryRowStatus", key],
                    },
                ]
        return r

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
            elif not p.get("vendor"):
                self.logger.debug("[%s] Empty Vendor Properties. Skipping...", match["sec_name"])
                continue
            r += [
                self.inventory_item(
                    **{
                        "name": match["sec_name"],
                        "num": int(match["num"] or 0),
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

    tc_type_map = {"767": "BOARD", "146021": "BOARD"}

    def get_ma5600_subboard(self):
        # SubBoard
        subboard = defaultdict(list)
        for slot_index, slot_type, slot_ver, slot_descr in self.snmp.get_tables(
            [
                mib["HUAWEI-DEVICE-MIB::hwSubslotType"],
                mib["HUAWEI-DEVICE-MIB::hwSubslotVersion"],
                mib["HUAWEI-DEVICE-MIB::hwSubSlotDesc"],
            ],
            bulk=False,
        ):
            if not slot_descr:
                continue
            _, slot_num, board_num = slot_index.rsplit(".", 2)
            if board_num == "65535":
                continue
            part_no = slot_descr[:-1]
            subboard[int(slot_num)] += [
                {
                    "type": "SUBBOARD",
                    "number": board_num,
                    "vendor": "Huawei",
                    "part_no": part_no,
                    "description": slot_descr[:-1],
                }
            ]
        return subboard

    def execute_snmp(self, **kwargs):
        """
        Slot part_no is not full (ex. ADFE)
        :param kwargs:
        :return:
        """
        r = []
        # Chassis
        for oid, frame_descr in self.snmp.getnext(mib["HUAWEI-DEVICE-MIB::hwFrameDesc"]):
            r += [
                {
                    "type": "CHASSIS",
                    "number": 0,
                    "vendor": "Huawei",
                    "part_no": frame_descr.split("_")[0],
                    "serial": None,
                    "description": "",
                    "mnf_date": None,
                }
            ]
        subboard = self.get_ma5600_subboard()
        # Slots
        for (
            slot_index,
            slot_type,
            slot_descr,
            slot_subs,
            slot_phys_serial,
        ) in self.snmp.get_tables(
            [
                mib["HUAWEI-DEVICE-MIB::hwSlotType"],
                mib["HUAWEI-DEVICE-MIB::hwSlotDesc"],
                mib["HUAWEI-DEVICE-MIB::hwSubSlots"],
                mib["HUAWEI-DEVICE-MIB::hwSlotPhySerialNum"],
            ],
            bulk=False,
        ):
            _, slot_num = slot_index.rsplit(".", 1)
            part_no, _, _ = slot_descr.split("_")
            r += [
                {
                    "type": self.tc_type_map.get(slot_type, "BOARD"),
                    "number": slot_num,
                    "vendor": "Huawei",
                    "part_no": part_no.strip(),
                    "serial": slot_phys_serial,
                    "description": slot_descr,
                }
            ]
            if int(slot_num) in subboard:
                r += subboard[slot_num]
        sensors = self.get_chassis_sensors()
        if r and sensors:
            r[0]["sensors"] = sensors
        return r

    def execute_inventory_board(self, **kwargs):
        """
        Uses if display elabel command unsupported
        :param kwargs:
        :return:
        """
        r = []
        serial = {}
        for oid, phys_num in self.snmp.getnext(
            mib["HUAWEI-DEVICE-MIB::hwSlotPhySerialNum"], bulk=False
        ):
            _, slot_num = oid.rsplit(".", 1)
            serial[int(slot_num)] = phys_num
        max_slot, boards = self.profile.get_board(self)
        for board in boards:
            r += [
                self.inventory_item(
                    **{
                        "name": "main_board",
                        "num": int(board["num"] or 0),
                        "parent": None,
                        "description": "",
                        "type": board["name"],
                        "vendor": "Huawei",
                        "barcode": serial[board["num"]],
                        "mnf_date": None,
                    }
                )
            ]
        return r

    def execute_cli(self, **kwargs):
        r = []
        subboards = None
        if self.is_dslam:
            # On MA5600 chassis and subboard serial is not supported
            # frame = self.cli("display frame info 0")
            part_no = "H511UPBA"  # MA5600
            descr = "MA5600's H511UPBA backplane, with double CELLBUS and GE bus"
            # Detect MA5600/MA5603
            slots, _ = self.profile.get_board(self)
            if slots == 7:
                part_no = "MA5603"
                descr = "MA5603 subrack"
            r += [
                {
                    "type": "CHASSIS",
                    "number": 0,
                    "vendor": "Huawei",
                    "part_no": part_no,
                    "serial": None,
                    "description": descr,
                }
            ]
            subboards = self.get_ma5600_subboard()
        with self.profile.diagnose(self):
            try:
                v = self.cli("display elabel 0", allow_empty_response=False)
                parse_result = self.parse_elabel(v)
            except self.CLISyntaxError:
                v = ""
        if not v:
            parse_result = self.execute_inventory_board()
        #     raise NotImplementedError("Not supported 'display elabel' command")
        for item in parse_result:
            self.logger.debug("Inventory item: %s", item)
            num = item.num
            item_name = item.name.lower()
            if self.is_builtin_service_chassis and (
                item_name.startswith("backplane") or item_name.startswith("main_board")
            ):
                # Dislike MA5801-GP16 has CHASSIS to Rack, SubRack and motherboard are same
                continue
            if self.is_builtin_service_chassis and item.name.startswith("port"):
                # MA5801-GP08/MA5801-GP16
                num = f"0/{item.parent[5:]}/{item.name[5:]}"
            if num == 0 and item.parent:
                num = int(item.parent.split("_")[-1])
            if item_name.startswith("port"):
                i_type = "XCVR"
            elif item_name.startswith("fan"):
                i_type = "FAN"
            elif item_name.startswith("slot") and "PWC" in item.type:
                i_type = "PWR"
            elif item.type.startswith("PDC") or "POWER BOARD" in item.description:
                i_type = "PWR"
            elif (
                "board" in item.description.lower() or item_name.startswith("main_board")
            ) and "Assembly Chassis" not in item.description:
                i_type = "BOARD"
            elif item_name.startswith("daughter_board"):
                i_type = "DAUGHTERBOARD"
            else:
                i_type = "CHASSIS"
            data = {
                "type": i_type,
                "number": num,
                "vendor": item.vendor,
                "part_no": item.type,
                "serial": item.barcode,
                "description": item.description,
            }
            if item.mnf_date:
                try:
                    mfg_date = parse(item.mnf_date)
                    data["mfg_date"] = mfg_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
            r += [data]
            if subboards and data["number"] in subboards:
                r += subboards[data["number"]]
        sensors = self.get_chassis_sensors()
        if r and sensors:
            r[0]["sensors"] = sensors
        return r
