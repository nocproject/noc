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


@dataclass
class Param(object):
    name: str
    value: str
    component: Optional[str]
    component_type: Optional[str]
    description: Optional[str]


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
