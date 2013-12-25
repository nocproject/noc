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
    pattern_zynos = r"^\S+?>"
    command_super = "enable"
    command_more = " "
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_exit = "exit"
    command_save_config = "write memory"
    command_enter_zynos = "mode zynos"
    command_exit_zynos = "sys cli newCLI"
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

    def zynos_mode(self, script):
        """Returns configuration context"""
        return ZyNOSContextManager(script)

    def setup_script(self, script):
        self.add_script_method(script, "zynos_mode", self.zynos_mode)


class ZyNOSContextManager(object):
    """zynos mode context manager to use with "with" statement"""
    def __init__(self, script):
        self.script = script
        self.profile = script.profile

    def __enter__(self):
        """Entering zynos mode context"""
        self.script.enter_config()
        self.script.push_prompt_pattern(self.script.profile.pattern_zynos)
        self.script.cli(self.profile.command_enter_zynos)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leaving zynos mode context"""
        if exc_type is None:
            self.script.pop_prompt_pattern()
            self.script.cli_provider.set_state("START")
            self.script.cli_provider.submit(self.profile.command_exit_zynos)
