# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple

# Third-party modules
import orjson

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from .profile import PolusParam, Component


@dataclass
class Device:
    pid: str
    address: int
    slot_name: str
    slot_number: int
    crate_id: int
    d_class: str


@dataclass
class FRU:
    part_no: str
    serial: str
    revision: Optional[str] = None
    type: str = "LINECARD"
    vendor: str = "IRE-Polus"

    # def parse_sensors(self, params: List[PolusParam]) -> List[Dict[str, Any]]:
    #     r = {}
    #     thresholds: List[PolusParam] = []
    #     port_states = {}
    #     for p in params:
    #         if p.is_threshold:
    #             thresholds.append(p)
    #             continue
    #         elif p.port and p.name == "State":
    #             port_states[p.port] = p.value != "Отсутствует"
    #             continue
    #         elif not p.is_metric:
    #             continue
    #         labels = []
    #         status = True
    #         if p.port:
    #             labels.append(f"port::{p.port}")
    #             labels.append(f"slot::{p.port}")
    #             status = port_states.get(p.port) or True
    #         if p.channel:
    #             labels.append(f"channel::{p.port}")
    #         if p.module:
    #             labels.append(f"module::{p.port}")
    #         r[(p.prefix, p.name)] = {
    #             "name": f"{p.prefix or ''}{p.name}",
    #             "status": status,
    #             "description": p.description,
    #             "measurement": p.get_measurement_unit,
    #             "labels": labels,
    #             "thresholds": [],
    #         }
    #     # print("TH", thresholds)
    #     for th in thresholds:
    #         if (th.prefix, th.name[:-4]) in r:
    #             r[(th.prefix, th.name[:-4])]["thresholds"] += [{
    #                 "id": f"{th.prefix or ''}{th.name}",
    #                 "value": th.value,
    #                 "realtion": "<=" if th.name.endswith("Min") else ">=",
    #                 "description": th.description,
    #             }]
    #     return list(r.values())


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_inventory"
    interface = IGetInventory

    rx_devices = re.compile(r"(?P<slot>\d+)\s*\|(?P<name>\S+)\s*")
    rx_table = re.compile(r"(?P<pname>\S+)\s*\|(?P<punits>\S*)\s*\|(?P<pvalue>.+)\s*")

    def get_fru(self, c: Component) -> Optional[FRU]:
        """
        Getting FRU from component info
        """
        r = FRU("", "")
        for p in c.info_params:
            if p.code == "PtNumber" or p.code == "pId":
                r.part_no = p.value
                r.type = p.component_type
            elif p.code == "SrNumber":
                r.serial = p.value
            elif p.code == "HwNumber":
                r.revision = p.value
            elif p.code == "Vendor":
                r.vendor = p.value
            # elif p.name == "State":
            #    r[component]["state"] = p.value != "Отсутствует"
        if r.serial:
            return r
        return None

    def get_sensors(
        self, c: Component, slot_num: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Getting Sensors from component metrics
        """
        r = []
        cfg_thresholds = []
        for p in c.metrics:
            labels, status = [], True
            if p.port:
                labels.append(f"noc::port::{p.port}")
                # status = port_states.get(p.port) or T
            # if p.channel:
            #     labels.append(f"channel::{p.channel}")
            if p.module:
                labels.append(f"noc::module::{p.module}")
            for tp in c.cfg_thresholds:
                if tp.name.startswith(p.name):
                    cfg_thresholds.append(
                        {
                            "param": tp.threshold_param,
                            "value": tp.value,
                            "scopes": [{"scope": "Sensor", "value": p.name}],
                            # "id": tp.name,
                            # "value": tp.value,
                            # "realtion": "<=" if tp.name.endswith("Min") else ">=",
                            # "description": tp.description,
                        }
                    )
            r += [
                {
                    "name": p.name,
                    "status": status,
                    "description": p.description,
                    "measurement": p.get_measurement_unit,
                    "labels": labels,
                    # "thresholds": thresholds,
                }
            ]
        return r, cfg_thresholds

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
        v = self.http.get("/api/crates/params?names=SrNumber,sysDevType", json=True)
        c = c["crates"][0]
        r += [
            {
                "type": "CHASSIS",
                "number": "1",
                "vendor": "IRE-Polus",
                "part_no": c["chassis"],
                # "serial": c_params["SrNumber"].value,
            }
        ]
        for p in v["params"]:
            p = PolusParam.from_code(**p)
            if p.code == "SrNumber":
                r[-1]["serial"] = p.value
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
        self.logger.debug(
            "Devices: %s",
            orjson.dumps(devices, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS).decode(
                "utf-8"
            ),
        )
        # /api/devices/params?crateId=1&slotNumber=3
        adapters = {}
        for slot, d in devices.items():
            v = self.http.get(
                f"/api/devices/params?crateId={d.crate_id}&slotNumber={slot}&fields=name,value,description",
                json=True,
            )
            adapter, num = None, d.slot_name
            if "." in num:
                adapter, num = num.split(".")
            elif num.startswith("CU"):
                num = num[-1]
            if adapter and adapter not in adapters:
                # H8 -> H4 card adapter
                r += [
                    {
                        "type": "LINECARD",
                        "number": adapter,
                        "vendor": "IRE-Polus",
                        "part_no": "HS-H8",
                    }
                ]
            params: List[PolusParam] = [PolusParam.from_code(**p) for p in v["params"]]
            self.logger.debug("[%s] Params: %s", num, [p for p in params if p.value])
            # Getting components
            components = Component.get_components(params=params)
            common = components["common"]
            c_fru = self.get_fru(common)
            sensors, cfgs = self.get_sensors(common, slot)
            for cc in common.cfg_params:
                if not cc.get_param_code():
                    continue
                cfgs.append(
                    {
                        "param": cc.get_param_code(),
                        "value": cc.value,
                        "scopes": cc.get_param_scopes(),
                    }
                )
            card = {
                "type": "LINECARD",
                "number": num,
                "vendor": "IRE-Polus",
                "part_no": c_fru.part_no,
                "serial": c_fru.serial,
                "revision": c_fru.revision,
                "sensors": sensors,
                "param_data": cfgs,
                "data": [{"interface": "hw_path", "attr": "slot", "value": str(slot)}],
                "crossing": [],
                # "param_data": self.get_cfg_param_data(common),
            }
            if common.crossing:
                for cross in common.crossing.values():
                    if not cross:
                        continue
                    if len(cross) < 2:
                        self.logger.info("Cross len lower than 2: [%s][%s]", len(cross), cross)
                        continue
                    c_in, c_out = cross[:2]
                    card["crossing"] += [
                        {
                            "input": c_in[0],
                            "input_discriminator": c_in[1],
                            "output": c_out[0],
                            "output_discriminator": c_out[1],
                            # "gain":
                        }
                    ]
            r += [card]
            for c_name, c in components.items():
                fru = self.get_fru(c)
                if c.is_common:
                    continue
                elif not fru:
                    sensors, cfgs = self.get_sensors(c, slot)
                    card["sensors"] += sensors
                    card["param_data"] += cfgs
                    if c.crossing:
                        for cross in c.crossing.values():
                            if len(cross) < 2:
                                self.logger.info(
                                    "Cross len lower than 2: [%s][%s]", len(cross), cross
                                )
                                continue
                            c_in, c_out = cross[:2]
                            card["crossing"] += [
                                {
                                    "input": c_in[0],
                                    "input_discriminator": c_in[1],
                                    "output": c_out[0],
                                    "output_discriminator": c_out[1],
                                    # "gain":
                                }
                            ]
                    for cc in c.cfg_params:
                        if not cc.get_param_code():
                            continue
                        card["param_data"].append(
                            {
                                "param": cc.get_param_code(),
                                "value": cc.value,
                                "scopes": cc.get_param_scopes(),
                            }
                        )
                    continue
                self.logger.debug("[%s] Parse FRU", fru)
                # card["param_data"] += self.get_cfg_param_data(c)
                sensors, cfgs = self.get_sensors(c, slot)
                card["sensors"] += sensors
                card["param_data"] += cfgs
                for cc in c.cfg_params:
                    if not cc.get_param_code():
                        continue
                    card["param_data"].append(
                        {
                            "param": cc.get_param_code(),
                            "value": cc.value,
                            "scopes": cc.get_param_scopes(),
                        }
                    )
                r += [
                    {
                        "type": fru.type,
                        "number": c.num,
                        "vendor": fru.vendor,
                        "part_no": fru.part_no,
                        "serial": fru.serial,
                        "revision": fru.revision,
                        # "sensors": sensors,
                        # "param_data": cfgs,
                    }
                ]
        return r

    def execute_cli(self, **kwargs):
        return self.execute_http(**kwargs)

    # def execute_cli(self):
    #     r = [{"type": "CHASSIS", "number": "1", "vendor": "Polus", "part_no": "K8"}]
    #     v = self.cli("show devices")
    #     for match in self.rx_devices.finditer(v):
    #         slot = match.group("slot")
    #         v = self.cli(f"show params {slot}")
    #         o = self.parse_table(v)
    #         r += [
    #             {
    #                 "type": "LINECARD",
    #                 "vendor": "IRE-Polus",
    #                 "number": slot,
    #                 "part_no": match.group("name"),
    #                 "serial": o["SrNumber"],
    #                 "revision": o["HwNumber"],
    #             }
    #         ]
    #     return r
