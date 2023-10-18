# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from dataclasses import dataclass
from typing import Dict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


@dataclass
class Device(object):
    pid: str
    address: int
    slot_name: str
    slot_number: int
    crate_id: int
    d_class: str


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_inventory"
    interface = IGetInventory

    rx_devices = re.compile(r"(?P<slot>\d+)\s*\|(?P<name>\S+)\s*")
    rx_table = re.compile(r"(?P<pname>\S+)\s*\|(?P<punits>\S*)\s*\|(?P<pvalue>.+)\s*")

    def parse_table(self, v):
        r = {}
        for match in self.rx_table.finditer(v):
            r[match.group("pname")] = match.group("pvalue").strip()
        return r

    def execute_http(self, **kwargs):
        r = []
        c = self.http.get("/api/crates", json=True)
        if not c:
            return
        c_params = self.http.get("/api/crates/params?names=SrNumber,sysDevType", json=True)
        c = c["crates"][0]
        # c_params = self.process_params(c_params["params"])
        c_params = self.profile.parse_params(c_params["params"])
        r += [
            {
                "type": "CHASSIS",
                "number": "1",
                "vendor": "IPG",
                "part_no": c["chassis"],
                "serial_no": c_params["SrNumber"].value,
            }
        ]
        # slots = self.http.get("/api/slots")
        devices: Dict[int, Device] = {}  # slot -> device info
        v = self.http.get("/api/devices", json=True)
        for item in v["devices"]:
            devices[item["slotNumber"]] = Device(
                **{
                    "pid": item["pid"],
                    "address": item["address"],
                    "slot_name": item["slotName"],
                    "slot_number": item["slotNumber"],
                    "crate_id": item["crateId"],
                    "d_class": item["class"],
                }
            )
        print(devices)
        # /api/devices/params?crateId=1&slotNumber=3
        cards = []
        for slot, d in devices.items():
            p = self.http.get(
                f"/api/devices/params?crateId={d.crate_id}&slotNumber={slot}&fields=name,value,description",
                json=True,
            )
            p = self.profile.parse_params(p["params"])
            if d.d_class == "":
                # cu card
                ...
        return r

    def execute(self, **kwargs):
        return self.execute_http(**kwargs)

    def execute_cli(self):
        r = [{"type": "CHASSIS", "number": "1", "vendor": "Polus", "part_no": "K8"}]
        v = self.cli("show devices")
        for match in self.rx_devices.finditer(v):
            slot = match.group("slot")
            v = self.cli(f"show params {slot}")
            o = self.parse_table(v)
            r += [
                {
                    "type": "LINECARD",
                    "vendor": "Polus",
                    "number": slot,
                    "part_no": match.group("name"),
                    "serial": o["SrNumber"],
                    "revision": o["HwNumber"],
                }
            ]
        return r
