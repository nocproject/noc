# ---------------------------------------------------------------------
# Vendor: HP
# OS:     Comware
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.Comware"
    command_more = " "
    command_exit = "quit"
    pattern_more = [(r"^\s*---- More ----$", " ")]
    pattern_prompt = r"[\n\s][<\[]\S+[>\]]"
    pattern_syntax_error = (
        r"% (?:Unrecognized command|Too many parameters|Incomplete command)" r" found at"
    )
    rogue_chars = [
        re.compile(br"\x1b\[16D\s+\x1b\[16D"),
        re.compile(br"\x1b\[42D\s+\x1b\[42D"),
        b"\r",
    ]

    spaces_rx = re.compile(r"^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)

    matchers = {
        "is_bad_release": {"version": {"$regex": r"2209P"}},
    }

    def clean_spaces(self, config):
        config = self.spaces_rx.sub("", config)
        return config

    INTERFACE_TYPES = {
        "Au": "physical",  # Aux
        "nu": "other",  # NULL
        "lo": "loopback",  # Loopback
        "in": "loopback",  # Loopback
        "vs": "SVI",  # vsi
        "vl": "SVI",  # Vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        if name.startswith("Bridge-Aggregation") or name.startswith("Route-Aggregation"):
            return "aggregated"
        elif name.startswith("LoopBack") or name.startswith("InLoopBack"):
            return "loopback"
        elif name.startswith("Vsi"):
            return "SVI"
        elif name.startswith("Vlan-interface"):
            return "SVI"
        elif name.startswith("Register"):
            return "other"
        elif name.startswith("NULL"):
            return "unknown"
        elif name.startswith("Aux"):
            return "other"
        else:
            return "physical"
