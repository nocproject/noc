# ---------------------------------------------------------------------
# Vendor: HP
# OS:     Comware
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.Comware"

    command_exit = "quit"
    pattern_more = [(rb"^\s*---- More ----$", b" ")]
    pattern_prompt = rb"[\n\s][<\[]\S+[>\]]"
    pattern_syntax_error = (
        rb"% (?:Unrecognized command|Too many parameters|Incomplete command) found at"
    )
    rogue_chars = [
        re.compile(rb"\x1b\[16D\s+\x1b\[16D"),
        re.compile(rb"\x1b\[42D\s+\x1b\[42D"),
        b"\r",
    ]

    spaces_rx = re.compile(r"^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)

    matchers = {
        "is_bad_release": {"version": {"$regex": r"2209P"}},
    }

    def clean_spaces(self, config):
        return self.spaces_rx.sub("", config)

    INTERFACE_TYPES = {
        "Au": "physical",  # Aux
        "nu": "other",  # NULL
        "lo": "loopback",  # Loopback
        "in": "loopback",  # Loopback
        "vs": "SVI",  # vsi
        "vl": "SVI",  # Vlan
    }

    rx_interface_name = re.compile(
        r"^(?P<type>GE|XGE|FGE|MGE|BAGG|Loop|InLoop|REG|RAGG|Tun|Vsi|Vlan-Int)"
        r"(?P<number>[\d/]+(\.\d+)?)$"
    )

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("GE2/0/0")
        'GigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("XGE2/0/0")
        'Ten-GigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("BAGG2")
        'Bridge-Aggregation2'
        """
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        return "%s%s" % (
            {
                "GE": "GigabitEthernet",
                "XGE": "Ten-GigabitEthernet",
                "FGE": "FortyGigE",
                "MGE": "M-GigabitEthernet",
                "BAGG": "Bridge-Aggregation",
                "Loop": "LoopBack",
                "InLoop": "InLoopBack",
                "REG": "Register-Tunnel",
                "RAGG": "Route-Aggregation",
                "Tun": "Tunnel",
                "Vsi": "Vsi-interface",
                "Vlan-int": "Vlan-interface",
            }[match.group("type")],
            match.group("number"),
        )

    @classmethod
    def get_interface_type(cls, name):
        if name.startswith("Bridge-Aggregation") or name.startswith("Route-Aggregation"):
            return "aggregated"
        if name.startswith("LoopBack") or name.startswith("InLoopBack"):
            return "loopback"
        if name.startswith("Vsi") or name.startswith("Vlan-interface"):
            return "SVI"
        if name.startswith("NULL"):
            return "null"
        if name.startswith("Tun") or name.startswith("Register-Tunnel"):
            return "tunnel"
        if name.startswith("Aux"):
            return "other"
        return "physical"
