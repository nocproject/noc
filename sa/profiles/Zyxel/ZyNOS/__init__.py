# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zyxel
## OS:     ZyNOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Zyxel.ZyNOS"
    supported_schemes = [TELNET, SSH]
    pattern_username = "User name:"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_prompt = r"^\S+?#"
    pattern_more = r"^-- more --.*?$"
    command_super = "enable"
    command_more = " "
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_exit = "exit"
    command_save_config = "write memory"
    pattern_syntax_error = "Invalid (command|input)"
    config_volatile = [r"^time\s+(\d+|date).*?^"]
    rx_ifname = re.compile(r"^swp(?P<number>\d+)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("1")
        '1'
        >>> Profile().convert_interface_name("swp00")
        '1'
        """
        match = self.rx_ifname.match(s)
        if match:
            return "%d" % (int(match.group("number")) + 1)
        else:
            return s
