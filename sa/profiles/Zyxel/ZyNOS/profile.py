# ---------------------------------------------------------------------
# Vendor: Zyxel
# OS:     ZyNOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.ZyNOS"

    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_prompt = rb"^\S+?\s*(\S+|)#"
    pattern_more = [(rb"^-- more --.*?$", b" ")]
    pattern_zynos = rb"^\S+?>"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_exit = "exit"
    command_save_config = "write memory"
    command_enter_zynos = "mode zynos"
    command_exit_zynos = "sys cli newCLI"
    pattern_syntax_error = b"Invalid (command|input)"
    # enable_cli_session = False
    rogue_chars = [rb"\x1b7", b"\r"]
    config_volatile = [r"^time\s+(\d+|date).*?^"]
    rx_ifname = re.compile(r"^swp(?P<number>\d+)$")

    matchers = {
        "is_platform_2024": {"platform": {"$regex": r"2024"}},
        "is_platform_2108": {"platform": {"$regex": r"2108"}},
        "is_version_3_90": {"version": {"$regex": r"^3\.90.*"}},
        "is_version_4_xx": {"version": {"$regex": r"^4\..*"}},
    }

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
            self.script.cli(self.profile.command_exit_zynos)
