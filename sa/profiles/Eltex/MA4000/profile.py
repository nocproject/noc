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

    pattern_username = rb"^\S+ login: "
    pattern_more = [(rb"^--More-- ", b" "), (rb"\[Yes/press any key for no\]", b"Y")]
    rogue_chars = [
        re.compile(rb"\r\s{9}\r"),
        re.compile(rb"^\s+VLAN Table\r\n\s+\~+\r\n", re.MULTILINE),
        b"\r",
    ]
    pattern_syntax_error = rb"^Unknown command"
    pattern_prompt = rb"^(?P<hostname>\S+)# "
    command_exit = "exit"
    telnet_naws = b"\x00\x7f\x00\x7f"

    def convert_interface_name(self, interface):
        return " ".join(interface.split())
