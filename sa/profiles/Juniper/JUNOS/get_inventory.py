# ---------------------------------------------------------------------
# Juniper.JUNOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.validators import is_int


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
    }

    ENV_TYPE_MAP = {"power": "supply", "temp": "temperature", "fans": "fan"}

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
        for line in response.splitlines():
            line = line.strip()
            if not line:
                continue

            match = self.env_part.search(line)

            if match:
                yield match.groups()

    def get_sensors(self):
        res = {}
        chassis_environment_response = self.cli("show chassis environment", cached=True)

        p_chassis_environment = self.parse_chassis_environment(chassis_environment_response)

        for env_type, env_name, env_status in p_chassis_environment:
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
        sensors = self.get_sensors()
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
