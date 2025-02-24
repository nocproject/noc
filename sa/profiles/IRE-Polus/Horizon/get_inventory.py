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
from noc.core.discriminator import LambdaDiscriminator


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
    fw_version: Optional[str] = None
    type: str = "LINECARD"
    vendor: str = "IRE-Polus"
    is_rbs: bool = False

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

    @staticmethod
    def get_port(n: str) -> str:
        """
        Convert port name:
            Cl_1 -> CLIENT1
            Ln_1 -> LINE1
        """
        t, n = n.split("_", 1)
        if t == "Cl":
            return f"CLIENT{n}"
        elif t == "Ln":
            return f"LINE{n}"
        raise ValueError(f"Invalid port {n}")

    @staticmethod
    def get_raw_port(n: str) -> str:
        """
        Clean port name from crossing:
            Cl_5_ODU2 -> Cl_5
        """
        t, n, _ = n.split("_", 2)
        return "_".join([t, n])

    @staticmethod
    def convert_datatype_to_odu(datatype: str) -> str:
        OTU_MAP = {
            "OTUC6": "ODUC6",
            "OTUC5": "ODUC5",
            "OTUC4": "ODUC4",
            "OTUC3": "ODUC3",
            "OTUC2": "ODUC2",
            "OTUC1": "ODUC1",
            "OTU4": "ODU4",
            "OTU3": "ODU3",
            "OTU2e": "ODU2e",
            "OTU2": "ODU2",
            "OTU1": "ODU1",
        }

        if datatype in OTU_MAP:
            return OTU_MAP[datatype]
        else:
            raise ValueError(f"datatype {datatype} is not in map")

    @staticmethod
    def get_default_datatype(mode: str, port: str) -> str:
        """
        Returns default datatype for card ADM-200 on port in different mode
        """
        DEFAULT_DATATYPE_MAP = {
            "AGG-200": {
                "LINE1": "OTUC2",
                "LINE2": "OTUC2",
            },
            "AGG-100-BS": {
                "LINE1": "OTU4",
                "LINE2": "OTU4",
            },
            "AGG-2x100": {
                "LINE1": "OTU4",
                "LINE2": "OTU4",
            },
            "TP-100+TP-10x10": {
                "LINE1": "OTU4",
                "LINE2": "OTU4",
                "CLIENT11": "OTU2",
                "CLIENT12": "OTU2",
                "CLIENT13": "OTU2",
                "CLIENT14": "OTU2",
                "CLIENT15": "OTU2",
                "CLIENT16": "OTU2",
                "CLIENT17": "OTU2",
                "CLIENT18": "OTU2",
                "CLIENT19": "OTU2",
                "CLIENT20": "OTU2",
            },
        }

        if mode in DEFAULT_DATATYPE_MAP:
            if port in DEFAULT_DATATYPE_MAP[mode]:
                return DEFAULT_DATATYPE_MAP[mode][port]
            else:
                raise ValueError(f"Unknown port {port} in mode {mode}")
        else:
            raise ValueError(f"Unknown mode {mode}")

    @staticmethod
    def get_outer_odu(card_mode: str, dst_port: str, dst_datatype: str) -> str:
        if not dst_datatype:
            dst_datatype = Script.get_default_datatype(card_mode, dst_port)

        return Script.convert_datatype_to_odu(dst_datatype)

    @staticmethod
    def get_discriminator(outer_odu: str, code_dst: str) -> str:
        dst_odu = code_dst
        dst_discriminator = code_dst
        if "_" in code_dst:
            dst_odu, dst_n = code_dst.split("_")
            dst_discriminator = f"{dst_odu}-{dst_n}"

        if outer_odu == dst_odu:
            return f"odu::{dst_odu}"

        return f"odu::{outer_odu}::{dst_discriminator}"

    def get_fru(self, c: Component) -> Optional[FRU]:
        """
        Getting FRU from component info
        """

        def fix_fru(s: str) -> str:
            """
            Fix FRU.

            One morbid vendor tends to mix latin with cyrillic.
            Fix and relax.
            """
            return s.replace("С", "C").replace("с", "c")

        r = FRU("", "")
        for p in c.info_params:
            if p.code == "PtNumber" or p.code == "pId":
                if p.value.startswith("RBS-"):
                    r.is_rbs = True
                    r.part_no = fix_fru(p.value[4:])
                else:
                    r.part_no = fix_fru(p.value)
                r.type = p.component_type
            elif p.code == "SrNumber":
                r.serial = p.value
            elif p.code == "HwNumber":
                r.revision = p.value
            elif p.code == "SwNumber":
                r.fw_version = p.value
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

    def parse_cross_roadm2x9(self, config) -> List[Dict[str, str]]:
        src: Dict[str, str] = {}
        dst: Dict[str, str] = {}
        gain: Dict[str, str] = {}
        crossings = []

        for oo in config:
            if "nam" not in oo or "val" not in oo:
                continue
            name = oo["nam"]

            if name.endswith("SetIn"):
                if not oo["val"] or oo["val"] == "Blocked" or oo["val"] == "Заблокирован":
                    continue
                src[name[:-5]] = oo["val"]

            if name.endswith("SetOut"):
                if not oo["val"] or oo["val"] == "Blocked" or oo["val"] == "Заблокирован":
                    continue
                dst[name[:-6]] = oo["val"]

            if name.endswith("SetOutAtt"):
                gain[name[:-9]] = oo["val"]

        for cname in dst:
            out_port = dst[cname]

            crossings.append(
                {
                    "input": "COM_IN",
                    "output": out_port,
                    "input_discriminator": str(LambdaDiscriminator.from_channel(cname)),
                }
            )

        for cname in src:
            in_port = src[cname]
            out_gain = gain.get(cname)

            crossings.append(
                {
                    "input": in_port,
                    "output": "COM_OUT",
                    "input_discriminator": str(LambdaDiscriminator.from_channel(cname)),
                    "gain_db": out_gain if out_gain else 1,
                }
            )

        return crossings, None

    def parse_cross_roadm2(self, config) -> List[Dict[str, str]]:
        client_src: List[str] = []
        dir_src: List[str] = []

        gain: Dict[str, str] = {}
        out_gain = 0
        crossings = []

        for oo in config:
            if "nam" not in oo or "val" not in oo:
                continue
            name = oo["nam"]

            if name.endswith("SetIn"):
                if not oo["val"] or oo["val"] == "Blocked" or oo["val"] == "Заблокирован":
                    continue
                if oo["val"] == "Клиент" or oo["val"] == "Client":
                    client_src.append(name[:-5])
                if oo["val"] == "Транзит" or oo["val"] == "Tranzit":
                    dir_src.append(name[:-5])

            if name.endswith("SetAtt"):
                gain[name[:-6]] = oo["val"]

            if name == "ClOutSetAtt":
                out_gain = oo["val"]

        # Cl In, Dir In --> Line Out
        for cname in client_src:
            crossings.append(
                {
                    "input": "CL IN",
                    "output": "LINE_OUT",
                    "input_discriminator": str(LambdaDiscriminator.from_channel(cname)),
                    "gain_db": gain.get(cname, 0),
                }
            )
            crossings.append(
                {
                    "input": "CL IN",
                    "output": "MON",
                    "input_discriminator": str(LambdaDiscriminator.from_channel(cname)),
                    "gain_db": gain.get(cname, 0),
                }
            )
        for cname in dir_src:
            crossings.append(
                {
                    "input": "DIR IN",
                    "output": "LINE_OUT",
                    "input_discriminator": str(LambdaDiscriminator.from_channel(cname)),
                }
            )
            crossings.append(
                {
                    "input": "DIR IN",
                    "output": "MON",
                    "input_discriminator": str(LambdaDiscriminator.from_channel(cname)),
                }
            )

        # Line In --> Cl Out / Dir Out
        crossings.append(
            {
                "input": "LINE_IN",
                "output": "CL OUT",
                "gain_db": out_gain,
            }
        )
        crossings.append(
            {
                "input": "LINE_IN",
                "output": "DIR OUT",
            }
        )

        return crossings, None

    def parse_cross_atp(self, config) -> List[Dict[str, str]]:
        src: Dict[str, str] = {}
        dst: Dict[str, str] = {}
        datatypes: Dict[str, str] = {}
        port_states: Dict[str, str] = {}
        mode: Optional[str] = None
        enable_oduflex = set()
        crossings = []

        for oo in config:
            if "nam" not in oo or "val" not in oo:
                continue
            name = oo["nam"]
            if name.endswith("_SetState"):
                # IS - In Service
                # OOS - Out Of Service
                # MT - Maintenance
                port_states[self.get_port(name[:-9])] = oo["val"] in ["IS", "MT"]
            if name.endswith("_SetSrc"):
                if oo["val"] != "None":
                    src[name[:-7]] = oo["val"]
            elif name.endswith("_SetDst"):
                if oo["val"] != "None":
                    dst[name[:-7]] = oo["val"]
            elif name == "SetMode":
                mode = oo["val"]
            elif name.endswith("_SetDataType"):
                if "GFC" in oo["val"]:
                    enable_oduflex.add(name[:-12])
                datatypes[self.get_port(name[:-12])] = oo["val"]

        for cname in src:
            if cname not in dst:
                continue

            input = self.get_port(self.get_raw_port(src[cname]))
            output = self.get_port(self.get_raw_port(dst[cname]))
            rest_dst = dst[cname].split("_", 2)[-1]

            datatype = datatypes[output]
            outer_odu = self.get_outer_odu(mode, output, datatype)

            if cname in enable_oduflex and rest_dst != "ODUFlex":
                continue
            if cname not in enable_oduflex and rest_dst == "ODUFlex":
                continue

            if port_states[input] and port_states[output]:
                crossings.append(
                    {
                        "input": input,
                        "output": output,
                        "output_discriminator": self.get_discriminator(outer_odu, rest_dst),
                    }
                )
            else:
                self.logger.debug(
                    "One of the ports is offline %s:%s,%s:%s",
                    input,
                    port_states[input],
                    output,
                    port_states[output],
                )

        return crossings, None

    def parse_cross_adm200(self, config) -> List[Dict[str, str]]:
        src: Dict[str, str] = {}
        dst: Dict[str, str] = {}
        datatypes: Dict[str, str] = {}
        port_states: Dict[str, str] = {}
        mode: Optional[str] = None
        enable_oduflex = set()
        crossings = []
        card_mode = None

        # Find card mode for parametrized crossing
        # For all ADM200 modes returns empty crossing except ADM-100
        # ADM-100 is configurable mode
        for oo in config:
            if "nam" not in oo or "val" not in oo:
                continue
            name = oo["nam"]
            value = oo["val"]
            if name == "SetMode":
                card_mode = value
                if card_mode != "ADM-100":
                    return crossings, card_mode

        # Parse crossings
        for oo in config:
            if "nam" not in oo or "val" not in oo:
                continue
            name = oo["nam"]
            value = oo["val"]
            if name.endswith("_SetState"):
                # IS - In Service
                # OOS - Out Of Service
                # MT - Maintenance
                port_states[self.get_port(name[:-9])] = value in ["IS", "MT"]
            if name.endswith("_SetSrc"):
                if value != "None":
                    src[name[:-7]] = value
            elif name.endswith("_SetDst"):
                if value != "None":
                    dst[name[:-7]] = value
            elif name == "SetMode":
                mode = value
            elif name.endswith("_SetDataType"):
                if "GFC" in value:
                    enable_oduflex.add(name[:-12])
                datatypes[self.get_port(name[:-12])] = value

        for cname in src:
            if cname not in dst:
                continue

            input = self.get_port(self.get_raw_port(src[cname]))
            output = self.get_port(self.get_raw_port(dst[cname]))
            rest_dst = dst[cname].split("_", 2)[-1]

            datatype = datatypes[output]
            outer_odu = self.get_outer_odu(mode, output, datatype)

            if cname in enable_oduflex and rest_dst != "ODUFlex":
                continue
            if cname not in enable_oduflex and rest_dst == "ODUFlex":
                continue

            crossings.append(
                {
                    "input": input,
                    "output": output,
                    "output_discriminator": self.get_discriminator(outer_odu, rest_dst),
                }
            )

        return crossings, card_mode


    def parse_cross_default(self, config) -> List[Dict[str, str]]:
        src: Dict[str, str] = {}
        dst: Dict[str, str] = {}
        datatypes: Dict[str, str] = {}
        port_states: Dict[str, str] = {}
        mode: Optional[str] = None
        enable_oduflex = set()
        crossings = []

        for oo in config:
            if "nam" not in oo or "val" not in oo:
                continue
            name = oo["nam"]
            if name.endswith("_SetState"):
                # IS - In Service
                # OOS - Out Of Service
                # MT - Maintenance
                port_states[self.get_port(name[:-9])] = oo["val"] in ["IS", "MT"]
            if name.endswith("_SetSrc"):
                if oo["val"] != "None":
                    src[name[:-7]] = oo["val"]
            elif name.endswith("_SetDst"):
                if oo["val"] != "None":
                    dst[name[:-7]] = oo["val"]
            elif name == "SetMode":
                mode = oo["val"]
            elif name.endswith("_SetDataType"):
                if "GFC" in oo["val"]:
                    enable_oduflex.add(name[:-12])
                datatypes[self.get_port(name[:-12])] = oo["val"]

        for cname in src:
            if cname not in dst:
                continue

            input = self.get_port(self.get_raw_port(src[cname]))
            output = self.get_port(self.get_raw_port(dst[cname]))
            rest_dst = dst[cname].split("_", 2)[-1]

            datatype = datatypes[output]
            outer_odu = self.get_outer_odu(mode, output, datatype)

            if cname in enable_oduflex and rest_dst != "ODUFlex":
                continue
            if cname not in enable_oduflex and rest_dst == "ODUFlex":
                continue

            crossings.append(
                {
                    "input": input,
                    "output": output,
                    "output_discriminator": self.get_discriminator(outer_odu, rest_dst),
                }
            )

        return crossings, None

    def get_crossings(
        self, config: Dict[str, Any], crate_num: int, slot: int
    ) -> List[Dict[str, str]]:
        card_mode = None
        crossings = []

        parser_mapping = {
            "atp": self.parse_cross_atp,
            "sroadm7": self.parse_cross_roadm2x9,
            "sroadm5": self.parse_cross_roadm2,
            "adm200": self.parse_cross_adm200,
        }

        for o in config["RK"][crate_num]["DV"]:
            if o["slt"] != slot:
                continue

            # print("###CLS###|%s|" % (o["cls"]))
            for cls_part in parser_mapping:
                if cls_part in o["cls"]:
                    return parser_mapping[cls_part](o["PM"])

            return self.parse_cross_default(o["PM"])

        return crossings, card_mode

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

        config = self.http.get(
            "/snapshots/full/config.json",
            json=True,
        )

        # /api/devices/params?crateId=1&slotNumber=3
        adapters = []
        for slot, d in devices.items():
            v = self.http.get(
                f"/api/devices/params?crateId={d.crate_id}&slotNumber={slot}&fields=name,value,description",
                json=True,
            )
            adapter, num = None, d.slot_name
            if "." in num:
                adapter, num = num.split(".")
            elif "-" in num:
                num, _ = num.split("-")
            elif num.startswith("CU"):
                num = num[-1]
            if adapter and adapter not in adapters:
                # H8 -> H4 card adapter
                r += [
                    {
                        "type": "ADAPTER",
                        "number": adapter,
                        "vendor": "IRE-Polus",
                        "part_no": "HS-H8",
                    }
                ]
                adapters.append(adapter)

            crossings, card_mode = self.get_crossings(config, d.crate_id - 1, slot)
            self.logger.debug("==|CROSS|==\n%s\n", crossings)

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
                "data": [
                    {"interface": "hw_path", "attr": "slot", "value": str(slot)},
                    {"interface": "asset", "attr": "fw_version", "value": c_fru.fw_version},
                ],
                "crossing": crossings,
                # "param_data": self.get_cfg_param_data(common),
            }
            if card_mode:
                card["mode"] = card_mode
            if adapter:
                card["type"] = "LINECARDH4"
            if common.crossing:
                for cross in common.crossing.values():
                    if not cross:
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
