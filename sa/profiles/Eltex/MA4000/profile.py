# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MA4000
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.MA4000"
    pattern_username = r"^\S+ login: "
    pattern_more = [(r"^--More-- ", " "), (r"\[Yes/press any key for no\]", "Y")]
    rogue_chars = [
        re.compile(r"\r\s{9}\r"),
        re.compile(r"^\s+VLAN Table\r\n\s+\~+\r\n", re.MULTILINE),
        "\r",
    ]
    pattern_syntax_error = r"^Unknown command"
    pattern_prompt = r"^(?P<hostname>\S+)# "
    command_exit = "exit"
    telnet_naws = b"\x00\x7f\x00\x7f"

    def convert_interface_name(self, interface):
        return " ".join(interface.split())
