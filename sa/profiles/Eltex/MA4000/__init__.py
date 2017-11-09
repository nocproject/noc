# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MA4000
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.MA4000"
    pattern_username = r"^\S+ login: "
    pattern_more = [
        (r"^--More-- ", " "),
        (r"\[Yes/press any key for no\]", "Y")
    ]
    rogue_chars = [
        re.compile(r"\r\s{9}\r"),
        re.compile(r"^\s+VLAN Table\r\n\s+\~+\r\n", re.MULTILINE),
        "\r"
    ]
    pattern_syntax_error = r"^Unknown command"
    pattern_prompt = r"^(?P<hostname>\S+)# "
    command_exit = "exit"
    telnet_naws = "\x00\x7f\x00\x7f"

    """
    @todo

    show interface plc-pon-port 8/0-7 vlans
    * PROGRAM ERROR (clish):
    Segmentation fault

    Fault address: 0xfffffffd

    Register dump:
     R0: fffffff9   R1: 413a54dc   R2: 406a3028   R3: 00000000
     R4: 400ec000   R5: 00000008   R6: 413a5564   R7: 00000001
     R8: 400cca2c   R9: 8ec6ba4c   SL: 00a624a8   FP: 41227d44
     IP: 406a2000   SP: 41227d20   LR: 413a54dc   PC: 405e4038
     CPSR: 20000010
     Trap: 0000000e   Error: 00000001   OldMask: 00001000
     Addr: fffffffd
    """
