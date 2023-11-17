# ---------------------------------------------------------------------
# Vendor: IRE-Polus
# OS:     Horizon
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# NOC modules
from noc.core.profile.base import BaseProfile


rx_case_component = re.compile(
    r"(pt|Module)?(?P<component>(PEM|FAN|Flash|Case|Crate|AirFilter|Port"
    r"|Ln|Dir|Cl|Line|Client|ASIC|PIC|ITLA|Pump)(In|Out)?\d?)(?P<name>\S+)$"
)

rx_transceiver = re.compile(r"\S+(?P<transiever>SFP|QSFP28|CFP2)\S+")
rx_port = re.compile(r"^((?:pt)?(?:Ln|Dir|Cl|Line|Client|PORT)(?:In|Out)?_?\d?)")
rx_channel = re.compile(r"\S+Lane_(\d+)\S+")


@dataclass
class Param(object):
    name: str
    value: str
    prefix: Optional[str] = None
    description: Optional[str] = None

    def __eq__(self, other: "Param") -> bool:
        if self.name == other.name and self.value == other.value and self.prefix == other.prefix:
            return True
        return False

    @property
    def component(self) -> str:
        # CARD, FAN, PEM, SFP, PORT, CASE, FLASH
        if not self.prefix:
            return "CARD"
        if self.port and rx_transceiver.match(self.prefix):
            # XCVR Detect
            # SFP, CFP2, QSFP28
            return "XCVR"
        elif self.port:
            return "PORT"
        elif self.prefix.startswith("FAN"):
            return "FAN"
        elif self.prefix.startswith("PEM"):
            return "PEM"
        return "CARD"

    @property
    def port(self) -> Optional[str]:
        # Line, Client, Port
        if not self.prefix:
            return None
        match = rx_port.match(self.prefix)
        if match:
            return match.groups()[0]
        return None

    @property
    def channel(self) -> Optional[str]:
        if self.prefix and rx_channel.match(self.prefix):
            return rx_channel.match(self.prefix).groups()[0]
        return None

    @classmethod
    def from_code(cls, name, value, description: Optional[str] = None, **kwargs) -> "Param":
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
        code, value, description = name.strip(), value.strip(), description.strip()
        if code.endswith("Max") or code.endswith("Min"):
            # Threshold param
            pass
        prefix, *param = code.rsplit("_", 1)
        if param:
            return Param(param[0], value, prefix=prefix, description=description)
        match = rx_case_component.match(code)
        if match:
            return Param(
                match.group("name"), value, match.group("component"), description=description
            )
        return Param(prefix, value, description=description)
        # Cl_*_QSFP28_Lane_@_TxPwr, Ln_#_CFP2_Temp,
        # if "XC" in prefix # CrossCommutation
        # raise ValueError("Unknown code")


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
        r"Ch\d+|[CH]\d+|ptAmp|Amp|(?:Cl|Ln)_\d+_SFP)\d*)?(?P<pname>\S+)"
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

    @classmethod
    def parse_params(
        cls, params: List[Dict[str, Any]], include_empty: bool = False
    ) -> Dict[str, Param]:
        """
        Parse params output from /params query

        :param params:
        :param include_empty: Include param with empty value
        """
        r = {}
        if isinstance(params, dict) and "params" in params:
            params = params["params"]
        for p in params:
            if not include_empty and not p["value"]:
                continue
            m = cls.rx_param.match(p["name"])
            component, ct, name = m.groups()
            name = name.strip("_")
            key = p["name"]
            if component:
                key = (component, name)
            r[key] = Param(
                **{
                    "value": p["value"].strip(),
                    "name": name,
                    "component": component,
                    "component_type": ct,
                    "description": p["description"],
                }
            )
        return r
