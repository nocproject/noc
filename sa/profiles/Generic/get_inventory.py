# ---------------------------------------------------------------------
# Generic.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python Modules
import datetime
import enum
from collections import defaultdict
from typing import Dict, List, Optional, Iterable
from dataclasses import dataclass

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.mib import mib


class EntityClass(enum.IntEnum):
    OTHER = 1
    UNKNOWN = 2
    CHASSIS = 3
    BACKPLANE = 4
    CONTAINER = 5
    POWERSUPPLY = 6
    FAN = 7
    SENSOR = 8
    MODULE = 9
    PORT = 10
    STACK = 11
    CPU = 12


class EntitySensorClass(enum.IntEnum):
    OTHER = 1
    UNKNOWN = 2
    VOLTSAC = 3
    VOLTSDC = 4
    AMPERES = 5
    WATTS = 6
    HERTZ = 7
    CELSIUS = 8
    PERCENTRH = 9
    RPM = 10
    CMM = 11
    TRUTHVALUE = 12


@dataclass
class SensorRow:
    name: str
    snmp_oid: str
    index: int
    units: str
    measurement: str


@dataclass
class EntityRow:
    type: EntityClass
    vendor: str
    part_no: str
    number: Optional[str] = None
    description: Optional[str] = None
    hw_rev: Optional[str] = None
    sw_rev: Optional[str] = None
    serial: Optional[str] = None
    mfg_date: Optional[datetime.datetime] = None
    ports: List["EntityRow"] = None
    sensors: List["SensorRow"] = None


class Script(BaseScript):
    name = "Generic.get_inventory"
    interface = IGetInventory

    EMPTY_VALUE = {"N/A", "UNKNOWN"}

    def get_sensor_labels(self) -> Dict[str, List[str]]:
        """
        For customizing. Return map sensor_name -> label.
        For sensor classification
        """
        return {}

    def get_chassis_sensors(self):
        """Return sensors on device chassis"""
        return []

    def clean_port_name(self, descr: str) -> str:
        """"""
        if "@" in descr:
            _, port = descr.split("@")
            return port.strip()

    def get_sensors(self, idx: Iterable[int]) -> Dict[int, List[SensorRow]]:
        # check_caps
        req_map = {
            mib["ENTITY-MIB::entPhysicalName"]: "name",
            mib["ENTITY-MIB::entPhysicalDescr"]: "descr",
            mib["ENTITY-MIB::entPhysicalContainedIn"]: "container",
        }
        data = self.snmp.get_chunked([f"{k}.{m}" for k in req_map for m in idx], chunk_size=10)
        sensors = defaultdict(dict)
        for oid, v in data.items():
            oid, index = oid.rsplit(".", 1)
            k = req_map[oid]
            sensors[int(index)][k] = v
        oper_status = {}
        for oid, v in self.snmp.getnext(mib["ENTITY-SENSOR-MIB::entPhySensorOperStatus"]):
            index, v = int(oid.rsplit(".", 1)[-1]), v
            oper_status[index] = v == 1
        r = defaultdict(list)
        for oid, v in self.snmp.getnext(mib["ENTITY-SENSOR-MIB::entPhySensorType"]):
            index, v = int(oid.rsplit(".", 1)[-1]), EntitySensorClass(v)
            s = {
                "name": sensors[index]["name"],
                "description": sensors[index].get("description"),
                "measurement": v,
                "status": oper_status[index],
                "snmp_oid": mib["ENTITY-SENSOR-MIB::entPhySensorValue", index],
            }
            parent = sensors[index]["container"]
            r[parent].append(s)
        return r

    def get_ports(self, idx: Iterable[int]):
        req_map = {
            mib["ENTITY-MIB::entPhysicalName"]: "name",
            mib["ENTITY-MIB::entPhysicalDescr"]: "descr",
            mib["ENTITY-MIB::entPhysicalContainedIn"]: "container",
            mib["ENTITY-MIB::entPhysicalIsFRU"]: "fru",
        }
        data = self.snmp.get_chunked([f"{k}.{m}" for k in req_map for m in idx], chunk_size=10)
        ports = defaultdict(dict)
        for oid, v in data.items():
            oid, index = oid.rsplit(".", 1)
            k = req_map[oid]
            ports[int(index)][k] = v
        r = defaultdict(list)
        for index, p in ports.items():
            if p["fru"] != 1:
                # port without FRU
                continue
            row = self.get_entity_row(index, EntityClass.PORT)
            # if not row.number and row.description:
            row.number = self.clean_port_name(row.description) or row.number
            r[p["container"]].append(
                {
                    "type": "XCVR",
                    "number": row.number,
                    "vendor": row.vendor,
                    "part_no": row.part_no,
                    # Serial number
                    "serial": row.serial,
                    "description": row.description,
                }
            )
        return r

    def get_entity_row(self, index: int, v_type: EntityClass) -> EntityRow:
        """Getting Entity-MIB record by index"""
        r = self.snmp.get(
            {
                "name": mib["ENTITY-MIB::entPhysicalName", index],
                "descr": mib["ENTITY-MIB::entPhysicalDescr", index],
                "hw_rev": mib["ENTITY-MIB::entPhysicalHardwareRev", index],
                "sw_rev": mib["ENTITY-MIB::entPhysicalSoftwareRev", index],
                "serial": mib["ENTITY-MIB::entPhysicalSerialNum", index],
                "vendor": mib["ENTITY-MIB::entPhysicalMfgName", index],
                "model_name": mib["ENTITY-MIB::entPhysicalModelName", index],
                "alias": mib["ENTITY-MIB::entPhysicalAlias", index],
                "mfg_date": mib["ENTITY-MIB::entPhysicalMfgDate", index],
                "container": mib["ENTITY-MIB::entPhysicalContainedIn", index],
            }
        )
        r = {k: v for k, v in r.items() if v not in self.EMPTY_VALUE}
        row = EntityRow(
            type=v_type,
            vendor=r["vendor"].upper(),
            part_no=r.get("model_name"),
            description=r["descr"],
            serial=r.get("serial"),
            number=r.get("name"),
            hw_rev=r.get("hw_rev"),
        )
        if r.get("mfg_date"):
            pass
        return row

    def get_entity_mib_inventory(self):
        """Process ENTITY-MIB"""
        hid_index: Dict[int, EntityClass] = {}
        pid_index: Dict[int, str] = {}
        sensors = set()
        modules = set()
        # v = self.scripts.get_version()
        vendor = "Aruba"
        for oid, v in self.snmp.getnext(mib["ENTITY-MIB::entPhysicalClass"]):
            _, index = oid.rsplit(".", 1)
            index, t = int(index), EntityClass(v)
            hid_index[index] = t
            if t == EntityClass.SENSOR:
                sensors.add(index)
            elif t == EntityClass.PORT:
                pid_index[index] = ""
            elif t == EntityClass.UNKNOWN:
                self.logger.info("[%s] Unknown module", index)
            elif t == EntityClass.CPU or t == EntityClass.CONTAINER:
                continue
            else:
                modules.add(index)
        # Sensors
        if sensors:
            sensors = self.get_sensors(sensors)
        self.logger.debug("Sensors: %s", sensors)
        # SFP Ports
        if pid_index:
            pid_index = self.get_ports(set(pid_index))
        self.logger.debug("Ports: %s", pid_index)
        out = []
        # Modules
        for m in modules:
            row = self.get_entity_row(m, hid_index[m])
            if not row.vendor:
                row.vendor = self.version["vendor"]
            if not row.part_no:
                self.logger.info("Unknown entity: %s", row.description)
                continue
            r = {
                "type": hid_index[m].name,
                "number": row.number,
                "vendor": row.vendor,
                "part_no": row.part_no,
                # Serial number
                "serial": row.serial,
            }
            if row.hw_rev:
                r["revision"] = row.hw_rev
            if row.mfg_date:
                r["mfg_date"] = row.mfg_date.isoformat()
            if row.description:
                r["description"] = row.description
            if m in sensors:
                r["sensors"] = sensors[m]
            out.append(r)
            if m not in pid_index:
                continue
            # Append ports
            for p in pid_index[m]:
                out.append(p)
        # print("RR", out)
        # Sensors
        return out

    def execute_snmp(self):
        return self.get_entity_mib_inventory()
