# ---------------------------------------------------------------------
# Vendor: IRE-Polus
# OS:     Horizon
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# NOC modules
from noc.core.profile.base import BaseProfile

# Modules:
# Amp1OSC - Канала служебной связи
# Amp1 - усилителя 1
# Amp1Att - VOA усилителя 1
# Amp1In - на входе усилителя 1
# Amp1OutSig - сигнала на выходе усилителя 1
# Amp1Pump1 - лазера накачки 1 усилителя 1
# BstAmpIn - входе бустера
# BstAmpOutSig - сигнала на выходе бустера
# BstAmpOut - на выходе бустера
# BstAmpPump - лазера накачки бустера
# PreAmpIn - входе предусилителя
# PreAmpOutSig - сигнала на выходе предусилителя
# PreAmpOut - на выходе предусилителя
# PreAmp - предусилителя
# PreAmpPump - лазера накачки предусилителя

rx_case_component = re.compile(
    r"(pt|Module)?(?P<component>(PEM|FAN|Flash|Case|Crate|AirFilter|Port"
    r"|Ln|Dir|Cl|Line|Client|ASIC|PIC|ITLA|Pump|FPGA)(In|Out)?\d*)(?P<name>\S+)$"
)

rx_transceiver = re.compile(r"\S+(?P<transiever>SFP|SFP\+|QSFP28|QSFP|CFP2)\S+")
rx_port = re.compile(
    r"^((?:pt)?(?:Ln|Dir|Cl|Line|Client|PORT|Port|OCM|Com|Mon|OUT|ChH|ChC|C\d+|H\d+)(?:In|Out)?_?\d*)"
)
rx_module = re.compile(
    r"^(Module)?(?P<module>Amp\d*|PreAmp|BstAmp|ASIC|FPGA|PIC\d*|TLA\d*|Pump\d*)(In|Out|OSC|Att|OutSig|Pump\d*)?"
)
rx_channel = re.compile(r"\S+Lane_(\d+)\S+")
rx_threshold = re.compile(r"(?P<param>\S+)(?P<type>CMax|WMax|WMin|CMin)$")
rx_num = re.compile(r"\S+(\d+)")
rx_cross_dst = re.compile(r"(?:ODU\d+)?(?P<port>(?:Ln|Cl|IN)_?\d+)(_(?P<odu>ODU\d+)(?P<odu_idx>_\d+))?")
rx_param_match = re.compile(
    r"(?:pt)?(?P<port>Ln_\d+|Cl_\d+|Line\d+|Client\d+|Port\d+|OSC|H\d+|C\d+)?(?P<c_name>\w+\d)*(\w*)"
    r"(?P<code>Set\S+|EnableTx|TxInfo|TxCat|RxCat|RxInfo|Source|Destination)"
)
rx_metric_match = re.compile(
    r"(?P<port>Ln_\d+|Cl_\d+|Line\d+|Client\d+|Port\d+)?(?P<c_name>\w+\d)*(\w*?)"
    r"(?P<direction>In|Out|Rx|Tx)?(?P<metric>OSCPwr|AttPwr|PwrDrift|Pwr|SigPwr|Att|Gain|GainTilt|ILD|ITEC|"
    r"Temp|Time|Speed|CPUUsage|MemLoad|DiskSpace|SNR|CD|DGD|Q|FECBER|EB|ES|SES|BBE|UAS|V)"
)

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
    "PwrDrift": "dB",
    "Att": "dB",
    "ILD": "A,m",
    "Gain": "dB",
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

THRESHOLD_PARAM_MAP = {
    "CMax": "threshold_c_max",
    "WMax": "threshold_w_max",
    "WMin": "threshold_c_min",
    "CMin": "threshold_w_min",
}


cfg_param_map = {
    "Destination": "port_destination",
    "SetTxFreqSp": "tx_frequency",
    "SetTxPwr": "tx_power",
    "EnableTx": "enable_tx",
    "SetState": "optical_state",
    "SetDataType": "otn_data_type",
    "SetFECType": "otn_fec_type",
    "SetPayload": "otn_payload",
}


@dataclass
class PolusParam:
    name: str
    value: str
    code: Optional[str] = None
    prefix: Optional[str] = None
    description: Optional[str] = None

    def get_param_scopes(self) -> Optional[List[Dict[str, str]]]:
        r = []
        match = rx_param_match.match(self.name)
        if not match:
            return None
        port, module, p_type, code = match.groups()
        if port and port.lower().startswith("ln"):
            r.append({"scope": "OpticalLinePort", "value": f"LINE{port[3:]}"})
        elif port and port.lower().startswith("cl"):
            r.append({"scope": "OpticalPort", "value": f"CLIENT{port[3:]}"})
        elif port and port.lower().startswith("po"):
            r.append({"scope": "EthernetPort", "value": f"Port{port[4:]}"})
        elif port and (port.lower().startswith("h") or port.lower().startswith("c")):
            r.append({"scope": "OpticalPort", "value": port})
        if port and module:
            r.append({"scope": "OTN", "value": module.strip("_")})
        # if port and p_type:
        #    r.append({"scope": "Module", "value": p_type.strip("_")})
        elif not port and module:
            r.append({"scope": "Module", "value": module.strip("_")})
        elif not port and p_type:
            r.append({"scope": "Module", "value": p_type.strip("_")})
        return r

    def get_param_code(self) -> Optional[str]:
        match = rx_param_match.match(self.name)
        if not match or match.group("code") not in cfg_param_map:
            return None
        return cfg_param_map[match.group("code")]

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
        self.name.startswith("Set")
        self.name.endswith("EnableTx")
        self.name.endswith("Cat")
        self.name.endswith("Info")
        """
        return bool(rx_param_match.match(self.name))

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
    def threshold_param(self) -> Optional[str]:
        if not self.is_threshold:
            return
        return THRESHOLD_PARAM_MAP[rx_threshold.match(self.name).group("type")]

    @property
    def get_measurement_unit(self) -> str:
        if self.name in METRIC_MAP:
            return METRIC_MAP[self.name]
        return "1"

    @property
    def is_cross(self) -> bool:
        return (
            self.name.endswith("SetSrc")
            or self.name.endswith("SetDst")
            or self.name.endswith("SetIn")
        )

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
        if self.port:
            return None
        match = rx_module.match(self.name)
        if match:
            return match.group("module")
        return None

    @classmethod
    def from_code(cls, name, value, description: Optional[str] = None, **kwargs) -> "PolusParam":
        """
        Parse param code

        >>> PolusParam.from_code("FAN1SrNumber", 0000)
        Param(name='SrNumber', value=0, prefix='FAN1', description=None)
        >>> PolusParam.from_code("FAN1State", 0)
        Param(name='State', value=0, prefix='FAN1', description=None)
        >>> PolusParam.from_code("DiskSpace", 0)
        Param(name='DiskSpace', value=0, prefix=None, description=None)
        >>> PolusParam.from_code("ClOutSetAtt", 0)
        Param(name='SetAtt', value=0, prefix='ClOut', description=None)
        >>> PolusParam.from_code("ptDirInCat", 0)
        Param(name='Cat', value=0, prefix='DirIn', description=None)
        >>> PolusParam.from_code("Cl_1_SetState", 0)
        Param(name='SetState', value=0, prefix='Cl_1', description=None)
        >>> PolusParam.from_code("Cl_1_SetState", 0).port
        'Cl_1'
        >>> PolusParam.from_code("ptDirInCat", 0).port
        'DirIn'
        >>> PolusParam.from_code("SetFactory", 0).port

        >>> PolusParam.from_code("Cl_2_QSFP28_Lane_3_RxPwr", -2).channel
        '3'
        >>> PolusParam.from_code("Cl_2_QSFP28_Lane_3_RxPwr", -2).component
        'XCVR'
        """
        name, value, description = name.strip(), value.strip(), description.strip()

        if name.endswith("Max") or name.endswith("Min"):
            # Threshold param
            pass
        if value == "None":
            value = None
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
    crossing: Dict[str, List[Tuple[str, str]]] = None

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

    def add_cross(self, p: PolusParam):
        if not p.value or p.value in ["Заблокирован", "Blocked"]:
            return
        # xc_index, xc_type = p.name.rsplit("_", 1)
        cross = rx_cross_dst.match(p.value).groupdict()
        d_port = cross["port"]
        d_odu = cross.get("odu")
        d_desc = cross.get("desc")
        if not d_port:
            print(f"Unknown port on crossing {p.value}")
            return
        if not d_odu:
            return
        if self.crossing is None:
            self.crossing = {}
        if p.prefix not in self.crossing:
            self.crossing[p.prefix] = []
        if d_desc:
            d_odu = f"odu::ODU2::{d_odu}-{d_desc.strip('_')}"
        else:
            d_odu = f"odu::ODU2::{d_odu}-0"
        if p.code == "SetSrc":
            self.crossing[p.prefix].insert(0, (d_port, d_odu))
        elif p.code == "SetDst":
            self.crossing[p.prefix].append((d_port, d_odu))

    @classmethod
    def get_components(cls, params: List[PolusParam]) -> Dict[str, "Component"]:
        r = {}
        ignored_components = set()

        for p in params:
            if p.value is None:
                continue
            c_name = p.component or "common"
            if c_name not in r:
                r[c_name] = Component(p.component, True, [], [], [], [])
            c = r[c_name]
            if p.is_info:
                c.info_params.append(p)
            elif p.is_threshold:
                c.cfg_thresholds.append(p)
#            elif p.is_cross:
#                c.add_cross(p)
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
            if "name" not in s or not s["name"].lower().startswith("cu") and "my" in s:
                continue
            return int(s["crateId"]), int(s["slotNumber"])
        raise script.NotSupportedError("Unknown Control Unit")

