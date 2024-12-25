# ---------------------------------------------------------------------
# Juniper.JUNOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import orjson

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.validators import is_int
from noc.core.mib import mib
from noc.core.snmp.error import SNMPError


class Script(BaseScript):
    name = "Juniper.JUNOS.get_inventory"
    interface = IGetInventory

    UNKNOWN_XCVR = "NoName | Transceiver | Unknown"

    rx_chassis = re.compile(
        r"^Chassis\s+(?P<revision>REV \d+)?\s+(?P<serial>\S+)\s+(?P<rest>.+)$", re.IGNORECASE
    )

    rx_part = re.compile(
        r"^\s*(?P<name>\S+(?: \S+)+?)\s+"
        r"(?P<revision>rev \d+|\S{1,6})?\s+"
        r"(?P<part_no>\d{3}-\d{6}|NON-JNPR|UNKNOWN|BUILTIN)\s+"
        r"(?P<serial>\S+)\s+"
        r"(?P<rest>.+)$",
        re.IGNORECASE,
    )

    env_part = re.compile(
        r"^(?P<type>(?:(?:Power|Temp|Fans))?\s+)?"
        r"(?P<name>(?:FPC(?:.\S+)+)\s+)"
        r"(?P<status>.\S+.)",
        re.IGNORECASE,
    )

    rx_num = re.compile(r"(?P<num>[0-9]/[0-9*])/*")

    TYPE_MAP = {
        "CHASSIS": "CHASSIS",
        "PEM": "PEM",
        "POWER SUPPLY": "PEM",
        "PDM": "PDM",  # Power Distribution Module
        "PSU": "PSU",
        "ROUTING ENGINE": "RE",
        "AFEB": "AFEB",
        "CB": "SCB",
        "MGMT BRD": "MGMT",
        "FPM BOARD": "FPM",  # Front Panel Display
        "QXM": "QXM",  # QX chip (Dense Queuing Block)
        "CPU": "CPU",  # MPC CPU
        "FPC": "FPC",
        "MPC": "FPC",
        "MIC": "MIC",
        "PIC": "PIC",
        "XCVR": "XCVR",
        "FTC": "FAN",
        "FAN TRAY": "FAN",
        "FAN": "FAN",
        "TFEB": "TFEB",
        "MIDPLANE": "MIDPLANE",
    }

    ENV_TYPE_MAP = {"power": "supply", "temp": "temperature", "fans": "fan"}

    ENV_TYPE_MAP_SNMP = {7: "supply", 13: "fan"}

    IGNORED = {
        "RE": {
            "710-015273",  # RE-J4350-2540
            "710-017560",  # RE-J2320-2000
            "750-021258",  # EX4200-24F
            "750-021778",  # RE-SRX210B
            "750-026331",  # EX2200-48P-4G, POE
            "750-026468",  # EX2200-24T-4G
            "750-033063",  # EX4200-48T, 8 POE
            "750-033065",  # EX4200-24T, 8 POE
            "750-033072",  # EX4200-48T, 8 POE
            "750-033073",  # EX4200-24T, 8 POE
            "750-033075",  # EX4200-24F
            "750-034594",  # RE-SRX210HE
            "750-036562",  # 750-036562
            "750-045404",  # EX4550-32F
        },
        "AFEB": {"BUILTIN"},  # Forwarding Engine Processor
    }

    def parse_hardware(self, v):
        """
        Parse "show chassis hardware"
        and yeld name, revision, part_no, serial, description
        """
        for line in v.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("node"):
                self.chassis_no = line[4:-1]
                continue
            match = self.rx_part.search(line)
            if match:
                yield match.groups()
            else:
                match = self.rx_chassis.search(line)
                if match:
                    rev = match.group("revision")
                    yield ("Chassis", rev, None, match.group("serial"), match.group("rest"))

    def parse_chassis_environment(self, response):
        response = "\n".join(response.split("\n")[1:])
        data = {}
        try:
            data = orjson.loads(response)
        except orjson.JSONDecodeError as e:
            self.logger.info("Error while parsing chassis environment %s", e)
            return

        env_info = data.get("environment-information")
        if not env_info:
            self.logger.info("environment-information is empty")

        env_items = env_info[0].get("environment-item")
        if not env_items:
            self.logger.info("environment-item is empty")

        for item in env_items:
            item_name = item["name"][0]["data"]
            item_status = item["status"][0]["data"]

            if item.get("class"):
                item_class = item["class"][0]["data"]
            else:
                continue

            yield item_class, item_name, item_status

    def get_sensors_cli(self):
        res = {}
        chassis_environment_response = self.cli("show chassis environment | display json", cached=True)

        p_chassis_environment = self.parse_chassis_environment(chassis_environment_response)

#        insert_type = None
        for env_type, env_name, env_status in p_chassis_environment:
            self.logger.info("|%s|%s|%s|", env_type, env_name, env_status)
            if env_type:
                insert_type = env_type.strip()
            chassis_id = env_name.split(" ")[1]
            env_status = env_status.strip().lower()
            if env_status == "absent":
                continue
            env_status = True if env_status == "ok" else False
            env_name = env_name.strip()

            sensor = {
                "name": f"{chassis_id}|{env_name}",
                "status": env_status,
                "description": f"State of {env_name} on Unit_{chassis_id}",
                "measurement": "StatusEnum",
                "labels": [
                    "noc::sensor::placement::internal",
                    "noc::sensor::mode::flag",
                    f"noc::sensor::target::{self.ENV_TYPE_MAP.get(insert_type.lower())}",
                    f"noc::chassis::{chassis_id}",
                ],
            }
            if res.get(chassis_id):
                res[chassis_id].append(sensor)
            else:
                res[chassis_id] = [sensor]

        return res

    def execute_cli(self):
        self.chassis_no = None
        self.virtual_chassis = None
        v = self.cli("show chassis hardware", cached=True)
        objects = []
        sensors = self.get_sensors_cli()
        chassis_sn = set()
        p_hardware = self.parse_hardware(v)

        for name, revision, part_no, serial, description in p_hardware:
            builtin = False
            # Detect type
            t, number = self.get_type(name)
            if not t:
                self.logger.error(
                    "Unknown module: %s %s %s %s %s", name, revision, part_no, serial, description
                )
                continue
            # Discard virtual chassis and ignored part numbers
            if description == "Virtual Chassis":
                self.virtual_chassis = True
                continue
            if t in self.IGNORED and part_no in self.IGNORED[t]:
                continue
            # Detect vendor
            if part_no in ("NON-JNPR", "UNKNOWN"):
                vendor = "NONAME"
            else:
                vendor = "JUNIPER"
            # Get chassis part number from description
            if t == "CHASSIS":
                part_no = description.split()[0].upper()
                if part_no.endswith(","):  # EX4200-48T, 8 POE
                    part_no = part_no[:-1]
                chassis_sn.add(serial)
            elif t == "FPC":
                if description.startswith("EX4"):
                    # Avoid duplicate `CHASSIS` type on some EX switches
                    has_chassis = False
                    if not self.virtual_chassis:
                        for i in objects:
                            if i["type"] == "CHASSIS":
                                has_chassis = True
                                break
                    if has_chassis:
                        continue
                    t = "CHASSIS"
                    part_no = description.split()[0].upper()
                    if part_no.endswith(","):  # EX4200-48T, 8 POE
                        part_no = part_no[:-1]
                    chassis_sn.add(serial)
            elif t == "XCVR":
                if vendor == "NONAME":
                    if description in ("UNKNOWN", "UNSUPPORTED"):
                        part_no = self.UNKNOWN_XCVR
                    else:
                        part_no = self.get_trans_part_no(serial, description)
            if serial == "BUILTIN" or serial in chassis_sn and t != "CHASSIS":
                builtin = True
                part_no = []
            if t == "CHASSIS" and number is None and self.chassis_no is not None:
                number = self.chassis_no
            if t in ["QXM", "CPU", "PDM"]:
                builtin = True

            obj = {
                "type": t,
                "number": number,
                "vendor": vendor,
                "serial": serial,
                "description": description,
                "part_no": part_no,
                "revision": revision,
                "builtin": builtin,
            }

            if obj["type"] == "CHASSIS":
                chassis_id = obj["number"] if obj.get("number") else "0"
                if sensor := sensors.get(chassis_id):
                    obj["sensors"] = sensor

            objects.append(obj)

        return objects

    def get_type(self, name):
        name = name.upper()
        n = name.split()
        if is_int(n[-1]):
            number = n[-1]
            name = " ".join(n[:-1])
        else:
            number = None
        return self.TYPE_MAP.get(name), number

    def get_trans_part_no(self, serial, description):
        """
        Try to detect non-juniper transceiver model
        """
        n = description.split()[0].split("-")
        if len(n) == 2:
            # SFP-LX, SFP-LH, SFP-EX, SFP-T
            t, m = n
            s = "1G"
            if m == "LX10":
                m = "LX"
        elif len(n) == 3:
            # SFP+-10G-LR, SFP+-10G-ER
            t, s, m = n
        elif len(n) == 4 and description.startswith("SFP-1000BASE-BX10-"):
            # SFP-1000BASE-BX10-U, SFP-1000BASE-BX10-D
            return "NoName | Transceiver | 1G | SFP BX10%s" % n[-1]
        elif len(n) == 4 and description.startswith("SFP-1000BASE-BX40-"):
            # SFP-1000BASE-BX40-U, SFP-1000BASE-BX40-D
            return "NoName | Transceiver | 1G | SFP BX%s" % n[-1]
        else:
            self.logger.error("Cannot detect transceiver type: '%s'", description)
            return self.UNKNOWN_XCVR
        return "NoName | Transceiver | %s | %s %s" % (s, t, m)

    def get_sensor_dict(self, chassis_id, env_name, env_status, sens_type_num, status_oid):
        sens_type = self.ENV_TYPE_MAP_SNMP.get(sens_type_num, "temperature")
        if sens_type_num in (7, 13):
            measur = "StatusEnum"
            descr = "State of "
        else:
            measur = "Celsius"
            descr = ""

        sensor = {
            "name": f"{chassis_id}|{env_name}",
            "status": env_status,
            "description": f"{descr}{env_name} on Unit_{chassis_id}",
            "measurement": measur,
            "labels": [
                "noc::sensor::placement::internal",
                "noc::sensor::mode::flag",
                f"noc::sensor::target::{sens_type}",
                f"noc::chassis::{chassis_id}",
            ],
            "snmp_oid": status_oid,
        }
        return sensor

    def get_sens_date(self, sens_oid):
        slotid = sens_oid[len(mib["JUNIPER-MIB::jnxFruType"]) + 1 :]
        chassis_id = str(int(slotid.split(".")[1]) - 1)
        env_status_oid = mib["JUNIPER-MIB::jnxFruState", slotid]
        env_status_num = self.snmp.get(env_status_oid)
        env_name = self.snmp.get(mib["JUNIPER-MIB::jnxFruName", slotid])
        return slotid, chassis_id, env_status_oid, env_status_num, env_name

    def update_sensors_dict(self, sensors_dict, chassis_id, sensor_dict):
        sensors_dict[chassis_id] = sensors_dict.get(chassis_id, []) + [sensor_dict]
        return sensors_dict

    def get_sensors_snmp(self):
        res = {}
        for oid, sens_type_num in self.snmp.getnext(mib["JUNIPER-MIB::jnxFruType"]):
            if sens_type_num in (13, 7):  # 13 - fan, 7 - power supply
                slotid, chassis_id, env_status_oid, env_status_num, env_name = self.get_sens_date(
                    oid
                )
                if env_status_num == 2:  # empty
                    continue
                elif env_status_num in (3, 4, 5, 6):
                    env_status = True
                else:
                    env_status = False
                sensor_dict = self.get_sensor_dict(
                    chassis_id, env_name, env_status, sens_type_num, env_status_oid
                )
                res = self.update_sensors_dict(res, chassis_id, sensor_dict)
        for oid, cur_temp in self.snmp.getnext(mib["JUNIPER-MIB::jnxOperatingTemp"]):  # temperature
            if cur_temp:
                slotid, chassis_id, env_status_oid, env_status_num, env_name = self.get_sens_date(
                    oid
                )
                env_name = f"Temperature {env_name}"
                env_status_num = bool(cur_temp)
                sensor_dict = self.get_sensor_dict(
                    chassis_id, env_name, env_status, sens_type_num, oid
                )
                res = self.update_sensors_dict(res, chassis_id, sensor_dict)
        return res

    def get_type_snmp(self, name):
        name = name.upper()
        n = name.rstrip("SLOT").strip().split()
        if is_int(n[-1]):
            number = n[-1]
        elif match := self.rx_num.search(name):
            number = match.group("num")
            while number[-1] in ("*", "/"):
                number = number.rstrip("*").rstrip("/")
            if "/" in number:
                number = number.split("/")[-1]
        else:
            number = "0"

        for key in self.TYPE_MAP.keys():
            if key in name:
                return self.TYPE_MAP.get(key), number

    def add_sensor_to_chassis(self, obj_dict, sensors_dict):
        if obj_dict["type"] == "CHASSIS":
            chassis_id = obj_dict.get("number")
            if sensor := sensors_dict.get(chassis_id):
                obj_dict["sensors"] = sensor

    def get_transceivers_snmp(self):
        transceivers = []
        for oid, voltage in self.snmp.getnext(
            mib["JUNIPER-DOM-MIB::jnxDomCurrentTxLaserOutputPower"]
        ):
            if voltage:
                ifindex = oid.split(".")[-1]
                ifname = self.snmp.get(mib["IF-MIB::ifDescr", ifindex])
                num_ifname = ifname.split("-")[-1].split(".")[0].replace("/", "").replace(":", ".")
                place_in_inv_lst = []
                for num in num_ifname:
                    if is_int(num):
                        num = str(int(num) + 1)
                    place_in_inv_lst.append(num)
                place_in_inv = float("".join(place_in_inv_lst))
                number = place_in_inv_lst[-1]

                obj = {
                    "type": "XCVR",
                    "number": number,
                    "vendor": "NONAME",
                    "serial": "NOSERIAL",
                    "description": "UNKNOWN",
                    "part_no": self.UNKNOWN_XCVR,
                    "builtin": False,
                }

                transceivers += [{"num_in_inv": place_in_inv, "obj": obj}]
        return transceivers

    def execute_snmp(self):
        self.chassis_no = None
        self.virtual_chassis = None
        objects = []
        chassis_sn = set()
        sensors = self.get_sensors_snmp()
        transc = self.get_transceivers_snmp()

        vendor_ch, part_no_ch = self.snmp.get(mib["JUNIPER-MIB::jnxBoxDescr", 0]).split()[:2]
        serial_ch = self.snmp.get(mib["JUNIPER-MIB::jnxBoxSerialNo", 0])

        revision_ch = ""
        try:
            revision_ch = self.snmp.get(mib["JUNIPER-MIB::jnxBoxRevision"])
        except SNMPError as e:
            self.logger.info("Error while retrieve revision: |%s|", e)

        chassis_obj = {
            "type": "CHASSIS",
            "number": "0",
            "vendor": vendor_ch,
            "serial": serial_ch,
            "description": part_no_ch,
            "part_no": part_no_ch,
            "revision": revision_ch,
            "builtin": False,
        }

        if "virtual chassis" in chassis_obj["description"].lower():
            self.virtual_chassis = True

        self.add_sensor_to_chassis(chassis_obj, sensors)
        chassis_sn.add(serial_ch)
        objects.append({"num_in_inv": 0, "obj": chassis_obj})

        for oid, description in self.snmp.getnext(mib["JUNIPER-MIB::jnxContentsDescr"]):
            if not description:
                continue
            builtin = False
            slotid = oid[len(mib["JUNIPER-MIB::jnxContentsContainerIndex"]) + 1 :]
            part_no = self.snmp.get(mib["JUNIPER-MIB::jnxContentsPartNo", slotid])
            serial = self.snmp.get(mib["JUNIPER-MIB::jnxContentsSerialNo", slotid])
            revision = self.snmp.get(mib["JUNIPER-MIB::jnxContentsRevision", slotid])
            slot_type_and_number = self.get_type_snmp(description)
            try:
                slot_type, number = slot_type_and_number
            except TypeError:
                continue  # unknown type

            num_in_inv = int("".join(slotid.split(".")[1:]))

            if not slot_type:
                self.logger.error(
                    f"Unknown module: {slot_type}, {revision}, {part_no}, {serial}, {description}"
                )
                continue

            if "Virtual Chassis" in description:
                self.virtual_chassis = True
                continue

            if slot_type in self.IGNORED and part_no in self.IGNORED[slot_type]:
                continue

            vendor = "NONAME" if part_no in ("NON-JNPR", "UNKNOWN") else "JUNIPER"

            if slot_type == "FPC" and description.startswith("EX4"):
                has_chassis = False
                if not self.virtual_chassis:
                    for i in objects:
                        if i["type"] == "CHASSIS":
                            has_chassis = True
                            break
                if has_chassis:
                    continue
                slot_type = "CHASSIS"
                part_no = description.split()[0].upper()
                if part_no.endswith(","):  # EX4200-48T, 8 POE
                    part_no = part_no[:-1]
                chassis_sn.add(serial)

            if serial == "BUILTIN" or serial in chassis_sn and slot_type != "CHASSIS":
                builtin = True
                part_no = []
            if slot_type == "CHASSIS" and number is None and self.chassis_no is not None:
                number = self.chassis_no
            if slot_type in ["QXM", "CPU", "PDM"]:
                builtin = True

            obj = {
                "type": slot_type,
                "number": number,
                "vendor": vendor,
                "serial": serial,
                "description": description,
                "part_no": part_no,
                "revision": revision,
                "builtin": builtin,
            }
            self.add_sensor_to_chassis(obj, sensors)
            objects.append({"num_in_inv": num_in_inv, "obj": obj})

        objects.extend(transc)
        objects_sort = [
            ob["obj"]
            for ob in sorted(
                objects,
                key=lambda x: (
                    x["num_in_inv"],
                    (
                        x["obj"]["description"]
                        if any(mod in x["obj"]["description"] for mod in ("MIC", "PIC"))
                        else ""
                    ),
                ),
            )
        ]
        return objects_sort
