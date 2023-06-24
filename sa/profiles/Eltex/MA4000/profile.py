# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MA4000
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.text import parse_table


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
    pattern_prompt = rb"^(?P<hostname>\S+?)(\(config\S*\))?# "
    command_enter_config = "configure terminal"
    command_exit = "exit"
    telnet_naws = b"\x00\x7f\x00\x7f"

    def convert_interface_name(self, interface):
        return " ".join(interface.split())

    def get_board(self, script):
        r = []
        v = script.cli("show shelf", cached=True)
        for i in parse_table(v):
            if i[2] == "none":
                continue
            r += [
                {
                    "slot": int(i[0]),
                    "version": i[3],
                    "serial": i[4],
                    "status": i[5],
                    "state": i[6],
                    "type": i[2],
                }
            ]
        return r
