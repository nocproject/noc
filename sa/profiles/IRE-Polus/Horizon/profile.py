# ---------------------------------------------------------------------
# Vendor: IRE-Polus
# OS:     Horizon
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# NOC modules
from noc.core.profile.base import BaseProfile


rx_case_component = re.compile(
    r"(pt|Module)?(?P<component>(PEM|FAN|Flash|Case|Crate|AirFilter|Port"
    r"|Ln|Dir|Cl|Line|Client|ASIC|PIC|ITLA|Pump|FPGA)(In|Out)?\d*)(?P<name>\S+)$"
)

rx_transceiver = re.compile(r"\S+(?P<transiever>SFP|SFP\+|QSFP28|CFP2)\S+")
rx_port = re.compile(
    r"^((?:pt)?(?:Ln|Dir|Cl|Line|Client|PORT|Port|OCM|Com|Mon|OUT|ChH|ChC|C\d+|H\d+)(?:In|Out)?_?\d*)"
)
rx_channel = re.compile(r"\S+Lane_(\d+)\S+")
rx_threshold = re.compile(r"(?P<param>\S+)(?P<type>CMax|WMax|WMin|CMin)$")
rx_num = re.compile(r"\S+(\d+)")

METRIC_MAP = {
    "Time": "s",
    "Temp": "C",
    "Alamrs": "1",
    "State": "1",
    "RxCD": "1",
    "RxDGD": "1",
    "RxPMD": "1",
    "RxQ": "1",
    "RxSNR": "1",
    "RxPwr": "dBm",
    "TxPwr": "dBm",
    "FECBER": "%",
    # Errors
    "EB": "1",
    "ES": "s",
    "SES": "s",
    "BBE": "1",
    "UAS": "s",
    #
    "RxPkts": "pkt",
    "RxOcts": "byte",
    "TxPkts": "pkt",
    "TxOcts": "byte",
    "TxErrs": "pkt",
    "RxErrs": "pkt",
    "SynbolRate": "bps",
    "PowerLed": "1",
    "AlarmLed": "1",
    "EnableTxLed": "1",
    "Speed": "1",
    "InV": "V",
    "InTemp": "C",
    "Power": "1",
    "MemLoad": "%",
    "DiskSpace": "byte",
    "CPUUsage": "%",
}

INFO_PARAMS = {
    "pid",
    "srnumber",
    "ptnumber",
    "swnumber",
    "hwnumber",
    "destination",
    "vendor",
    "minpwr",
    "maxpwr",
    "minfreq",
    "maxfreq",
    "freqsp",
}

STATE_MAP = {"Absent", "Ok"}


@dataclass
class PolusParam:
    name: str
    value: str
    code: Optional[str] = None
    prefix: Optional[str] = None
    description: Optional[str] = None

    @property
    def is_info(self) -> bool:
        """
        Check param is_info
        """
        return self.code.lower() in INFO_PARAMS

    @property
    def port(self) -> Optional[str]:
        """
        Return Port Name
        """
        # Line, Client, Port
        if not self.name:
            return None
        match = rx_port.match(self.name)
        if match:
            return match.groups()[0]
        return None

    @property
    def is_line(self) -> bool:
        """
        Check Param is lineport
        """
        return self.port and self.port.startswith("Ln")

    @property
    def is_client(self) -> bool:
        """
        Check param is Client Port
        """
        return self.port and self.port.startswith("Cl")

    @property
    def channel(self) -> Optional[str]:
        """
        Return if Channel Param
        """
        if self.prefix and rx_channel.match(self.prefix):
            return rx_channel.match(self.prefix).groups()[0]
        return None

    @property
    def is_config(self) -> bool:
        """
        Return if param is_config
        """
        if (
            self.name.startswith("Set")
            or self.name.endswith("EnableTx")
            or self.name.endswith("Cat")
            or self.name.endswith("Info")
        ):
            return True
        return False

    @property
    def is_metric(self) -> bool:
        """
        Check if param Is Metric
        """
        if self.is_config:
            return False
        if self.name in METRIC_MAP:
            return True
        if self.name.endswith("Alarms") or self.name.endswith("Temp"):
            return True
        return False

    @property
    def is_threshold(self) -> bool:
        match = rx_threshold.match(self.name)
        if not match:
            return False
        return True

    @property
    def get_measurement_unit(self) -> str:
        if self.name in METRIC_MAP:
            return METRIC_MAP[self.name]
        return "1"

    @property
    def component_type(self) -> Optional[str]:
        if rx_transceiver.match(self.name):
            return "XCVR"
        elif self.port:
            return "PORT"
        elif self.name.startswith("FAN"):
            return "FAN"
        elif self.name.startswith("PEM"):
            return "PEM"
        return "CARD"

    @property
    def component(self) -> Optional[str]:
        """
        Return Asset component for param
        """
        if self.port:
            return self.port
        if self.component_type == "CARD":
            return None
        match = rx_case_component.match(self.name)
        if match:
            return match.group("component")
        return

    @property
    def slot(self) -> Optional[str]:
        """
        Return Slot number
        """
        if self.port:
            return self.port[-1]

    @property
    def module(self) -> Optional[str]:
        """
        Return Module
        """
        if not self.name.startswith("Module"):
            return
        return self.name[6:-4]

    @classmethod
    def from_code(cls, name, value, description: Optional[str] = None, **kwargs) -> "PolusParam":
        """
        Parse param code

        >>> Param.from_code("FAN1SrNumber", 0000)
        Param(name='SrNumber', value=0, prefix='FAN1', description=None)
        >>> Param.from_code("FAN1State", 0)
        Param(name='State', value=0, prefix='FAN1', description=None)
        >>> Param.from_code("DiskSpace", 0)
        Param(name='DiskSpace', value=0, prefix=None, description=None)
        >>> Param.from_code("ClOutSetAtt", 0)
        Param(name='SetAtt', value=0, prefix='ClOut', description=None)
        >>> Param.from_code("ptDirInCat", 0)
        Param(name='Cat', value=0, prefix='DirIn', description=None)
        >>> Param.from_code("Cl_1_SetState", 0)
        Param(name='SetState', value=0, prefix='Cl_1', description=None)
        >>> Param.from_code("Cl_1_SetState", 0).port
        'Cl_1'
        >>> Param.from_code("ptDirInCat", 0).port
        'DirIn'
        >>> Param.from_code("SetFactory", 0).port

        >>> Param.from_code("Cl_2_QSFP28_Lane_3_RxPwr", -2).channel
        '3'
        >>> Param.from_code("Cl_2_QSFP28_Lane_3_RxPwr", -2).component
        'XCVR'
        """
        name, value, description = name.strip(), value.strip(), description.strip()

        if name.endswith("Max") or name.endswith("Min"):
            # Threshold param
            pass
        prefix, *param = name.rsplit("_", 1)
        if param:
            return PolusParam(name, value, code=param[0], prefix=prefix, description=description)
        match = rx_case_component.match(name)
        if match:
            return PolusParam(
                name, value, match.group("name"), match.group("component"), description=description
            )
        return PolusParam(name, value, prefix, description=description)


@dataclass
class Component:
    name: str
    state: bool
    metrics: List[PolusParam] = None
    cfg_thresholds: List[PolusParam] = None
    info_params: List[PolusParam] = None
    cfg_params: List[PolusParam] = None

    @property
    def is_common(self) -> bool:
        return not self.name or self.name == "common"

    @property
    def num(self) -> str:
        if not self.name:
            return ""
        match = rx_num.match(self.name)
        if match:
            return match.groups()[0]
        return ""

    @classmethod
    def get_components(cls, params: List[PolusParam]) -> Dict[str, "Component"]:
        r = {}
        ignored_components = set()
        for p in params:
            c_name = p.component or "common"
            if c_name not in r:
                r[c_name] = Component(p.component, True, [], [], [], [])
            c = r[c_name]
            if p.is_info:
                c.info_params.append(p)
            elif p.is_threshold:
                c.cfg_thresholds.append(p)
            elif p.is_config:
                c.cfg_params.append(p)
            elif p.is_metric:
                c.metrics.append(p)
            if p.code == "State" and not p.value and p.component:
                ignored_components.add(c_name)
        for ic in ignored_components:
            r.pop(ic)
        return r

    @classmethod
    def from_params(cls, params: List[Dict[str, str]]) -> Dict[str, "Component"]:
        params: List[PolusParam] = [PolusParam.from_code(**p) for p in params]
        return cls.get_components(params)


class Profile(BaseProfile):
    name = "IRE-Polus.Horizon"

    http_request_middleware = [
        "noc.sa.profiles.IRE-Polus.Horizon.middleware.horizonauth.HorizonAuthMiddeware",
    ]

    pattern_prompt = rb"(.+):>"
    command_exit = b"quit"
    rogue_chars = [b"\r", b"\\x1b", re.compile(rb"\[\d+;\d+m")]

    rx_param = re.compile(
        r"(?P<component>(FAN|ptOUT|Port|PEM|Case|Flash|MCU|OSC|"
        r"Ch\d+|[CH]\d+|ptAmp|Amp|(?:Cl|Ln)_\d+_([CS]FP?|ODU\d*|OTU?\d*|OPU\d*))\d*)?(?P<pname>\S+)"
    )

    @staticmethod
    def get_cu_slot(script) -> Tuple[int, int]:
        """
        Getting ControlUnit location
        """
        # get_capabilities Control Unit Slot
        slots = script.http.get("/api/slots", json=True, cached=True)
        # Getting ControlUnit
        for s in slots["slots"]:
            if not s["name"].lower().startswith("cu"):
                continue
            return int(s["crateId"]), int(s["slotNumber"])
        raise script.NotSupportedError("Unknown Control Unit")
