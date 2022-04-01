# ----------------------------------------------------------------------
# Vendor: NSN
# OS:     TIMOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NSN.TIMOS"

    pattern_username = rb"[Ll]ogin: "
    pattern_password = rb"[Pp]assword: "
    pattern_prompt = rb"^\S+?#"
    pattern_more = [(rb"^Press any key to continue.*$", b" ")]
    pattern_syntax_error = rb"Error: Bad command\.|Error: Invalid parameter\."
    command_disable_pager = "environment no more"
    command_exit = "logout"
    config_volatile = [r"^# Finished.*$", r"^# Generated.*$"]
    rogue_chars = [re.compile(rb"\r\s+\r"), b"\r"]
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "#", "end_of_context": "exit", "string_quote": '"'}

    rx_port_name = re.compile(r"(\d+\/\d+\/\d+)")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("0/1/1")
        '0/1/1'
        >>> Profile().convert_interface_name('port3/1/9, 10-Gig Ethernet, "--Description To 0/20/1"')
        '3/1/9'
        >>> Profile().convert_interface_name("port0/1/1")
        '0/1/1'
        """
        if self.rx_port_name.match(s):
            return s
        if "," in s:
            s = s.split(",", 1)[0].strip()
        if s.startswith("port"):
            s = s[4:]
        return s

    INTERFACE_TYPES = {
        "port": "physical",
        "lag-": "aggregated",
    }

    @classmethod
    def get_interface_type(cls, name):
        if cls.rx_port_name.match(name):
            return "physical"
        return cls.INTERFACE_TYPES.get(name[:4].lower())

    def get_linecard(self, interface_name):
        ifname = self.convert_interface_name(interface_name)
        return super().get_linecard(ifname)
