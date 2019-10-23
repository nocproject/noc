# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MES24xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.validators import is_int


class Profile(BaseProfile):
    name = "Eltex.MES24xx"
    pattern_more = [(r"--More--", " ")]
    pattern_prompt = r"(?P<hostname>\S+)#\s*"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)>\s*"
    pattern_syntax_error = r"^% Invalid (?:Command|input detected at)$"
    # command_disable_pager = "set cli pagination off"  - need conf t mode
    config_tokenizer = "line"
    config_tokenizer_settings = {"line_comment": "!"}
    command_submit = "\r"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    rogue_chars = [
        re.compile(r"\s*\x1b\[27m"),
        re.compile(r"\x1b\r\s+\r\x1b\[K"),
        re.compile(r"\x1b\[K"),
        re.compile(r"\r"),
    ]

    INTERFACE_TYPES = {
        "gi": "physical",  # gigabitethernet
        "fa": "physical",  # fastethernet
        "ex": "physical",  # extreme-ethernet
        "vl": "SVI",  # vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())

    # Eltex-like translation
    rx_eltex_interface_name = re.compile(
        r"^(?P<type>[a-z]{2})[a-z\-]*\s*"
        r"(?P<number>\d+(/\d+(/\d+)?)?(\.\d+(/\d+)*(\.\d+)?)?(:\d+(\.\d+)*)?(/[a-z]+\d+(\.\d+)?)?(A|B)?)?",
        re.IGNORECASE,
    )

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name_cisco("gi1/0/1")
        'Gi 1/0/1'
        >>> Profile().convert_interface_name_cisco("gi1/0/1?")
        'Gi 1/0/1'
        """
        if s.startswith("Slot"):
            # @todo InterfaceType check needed
            s = s.replace("Slot", "gigabitethernet")
        match = self.rx_eltex_interface_name.match(str(s))
        if is_int(s):
            return "Vl %s" % s
        elif s in ["oob", "stack-port"]:
            return s
        elif match:
            return "%s %s" % (match.group("type").capitalize(), match.group("number"))
        else:
            raise InterfaceTypeError("Invalid interface '%s'" % s)
