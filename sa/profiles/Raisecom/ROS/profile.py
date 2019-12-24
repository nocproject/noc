# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Raisecom
# OS:     ROS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.confdb.syntax.patterns import ANY


class Profile(BaseProfile):
    name = "Raisecom.ROS"
    pattern_more = r"^ --More--\s*"
    pattern_unprivileged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^\S+?#"
    command_more = " "
    command_exit = "exit"
    pattern_syntax_error = r"(% \".+\"  (?:Unknown command.)|Error input in the position marke[dt] by|%\s+Incomplete command\.)"
    pattern_operation_error = r"% You Need higher priority!"
    rogue_chars = [re.compile(r"\x08+\s+\x08+"), "\r"]
    config_volatile = [
        r"radius(-server | accounting-server |-)encrypt-key \S+\n",
        r"tacacs(-server | accounting-server |-)encrypt-key \S+\n",
    ]
    config_tokenizer = "context"
    config_tokenizer_settings = {
        "line_comment": "!",
        "contexts": [["interface", ANY, ANY]],
        "end_of_context": "!",
    }

    matchers = {
        "is_iscom2624g": {"platform": {"$regex": "ISCOM26(?:24|08)G"}},
        "is_rotek": {"vendor": {"$in": ["Rotek", "ROTEK"]}},
    }

    rx_port = re.compile(r"^port(|\s+)(?P<port>\d+)")

    def convert_interface_name(self, interface):
        if interface.startswith("GE"):
            return interface.replace("GE", "gigaethernet")
        if interface.startswith("FE"):
            return interface.replace("FE", "fastethernet")
        if self.rx_port.match(interface):
            match = self.rx_port.match(interface)
            return match.group("port")
        else:
            return interface

    INTERFACE_TYPES = {
        "nu": "null",  # NULL
        "fa": "physical",  # fastethernet
        "fe": "physical",  # fastethernet
        "gi": "physical",  # gigaethernet
        "ge": "physical",  # gigaethernet
        "lo": "loopback",  # Loopback
        "tr": "aggregated",  #
        "po": "aggregated",  # port-channel
        "mn": "management",  # Stack-port
        # "te": "physical",  # TenGigabitEthernet
        "vl": "SVI",  # vlan
        "un": "unknown",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2].lower())
