# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Nateks
# OS:     FlexGain
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile
import re


class Profile(BaseProfile):
    name = "Nateks.FlexGain"
    pattern_username = r"^\S+ login: "
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+):>"
    pattern_prompt = r"^(?P<hostname>\S+):%"
    pattern_more = r"^--More--"
    pattern_syntax_error = r"syntax error, unexpected STRING|Command Abort, More Arguments need!"
    command_super = "enable"
    command_more = "g"
    command_exit = "bye"
    rogue_chars = [re.compile(r" \(\[q\]Quit,\[g\]Go to end,\[any key\]Continue...\)\r\n"), "\r"]

    def convert_interface_name(self, interface):
        """
        Found on FG-ACE120 xDSL
        GigaBit Ethernet2
        Gigabit Ethernet 2
        """
        if interface.startswith("Giga"):
            return "GBE-" + interface.replace(" ", "")[15:]
        return interface
