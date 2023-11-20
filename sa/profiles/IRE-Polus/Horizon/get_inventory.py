# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from dataclasses import dataclass
from typing import Dict, List, Any
from collections import defaultdict

# Third-party modules
import orjson

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from .profile import Param


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

    cfg_params = {
        "SetTxFreqSp",
        "EnableTx",
        "SetState",
        "SetDataType",
        "SetFECType",
        "SetPayload",
        "SetPayload",
    }

    def parse_table(self, v):
        r = {}
        for match in self.rx_table.finditer(v):
            r[match.group("pname")] = match.group("pvalue").strip()
        return r

    def parse_components(self, params: Dict[str, Param]):
        r = {}
        for _, p in params.items():
            if p.component in r:
                continue
            if (
                p.component_type in {"FAN", "PEM"}
                and params[(p.component, "State")].value != "Отсутствует"
            ):
                r[p.component] = {
                    "type": p.component_type,
                    "number": p.component[-1],
                    "vendor": "IRE-Polus",
                    "part_no": params[(p.component, "PtNumber")].value,
                    "serial": params[(p.component, "SrNumber")].value,
                }
                if (p.component, "HwNumber") in params:
                    rev = params[(p.component, "HwNumber")].value
                    r[p.component]["revision"] = rev.split()[-1]
            elif (
                p.component
                and p.component.endswith("SFP")
                and params[(p.component, "State")].value == "Ok"
            ):
                r[p.component] = {
                    "type": "XCVR",
                    "number": p.component[-5],
                    "vendor": params[(p.component, "Vendor")].value,
                    "part_no": params[(p.component, "PtNumber")].value,
                    "serial": params[(p.component, "SrNumber")].value,
                }
        return list(r.values())

    def parse_components2(self, params: List[Param]) -> List[Dict[str, Any]]:
        r = defaultdict(dict)
        for p in params:
            if p.component in {"CARD", "PORT"}:
                continue
            component = (p.component, p.port)
            if component not in r:
                r[component]["vendor"] = "IRE-Polus"
            if p.name == "PtNumber":
                r[component]["part_no"] = p.value
            elif p.name == "SrNumber":
                r[component]["serial"] = p.value
            elif p.name == "HwNumber":
                r[component]["revision"] = p.value
            elif p.name == "Vendor":
                r[component]["vendor"] = p.value
            elif p.name == "State":
                r[component]["state"] = p.value != "Отсутствует"
        return list(r.values())

    def execute_http(self, **kwargs):
        r = []
        c = self.http.get("/api/crates", json=True)
        if not c:
            return
        v = self.http.get("/api/crates/params?names=SrNumber,sysDevType", json=True)
        c = c["crates"][0]
        # c_params = self.process_params(c_params["params"])
        # c_params = self.profile.parse_params(c_params["params"])
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
            p = Param.from_code(**p)
            if p.name == "SrNumber":
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
            # params: Dict[str, Param] = self.profile.parse_params(params["params"])
            # if params["pId"].value == "ADM-10-SFP/SFP+-H8":
            #    print(params)
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
            card = {
                "type": "LINECARD",
                "number": num,
                "vendor": "IRE-Polus",
                # "part_no": params["pId"].value,
                # "serial": params["SrNumber"].value,
                # "revision": params["HwNumber"].value,
            }
            params: List[Param] = []
            for p in v["params"]:
                p = Param.from_code(**p)
                if p.component == "CARD" and p.name == "pId":
                    card["part_no"] = p.value
                elif p.component == "CARD" and p.name == "SrNumber":
                    card["serial"] = p.value
                elif p.component == "CARD" and p.name == "HwNumber":
                    card["revision"] = p.value
                params.append(p)
            self.logger.debug("[%s] Params: %s", num, [p for p in params if p.value])
            r += [card]
            # r += self.parse_components(params)
            r += self.parse_components2(params)
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
