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
    pattern_username = "[Ll]ogin: "
    pattern_password = "[Pp]assword: "
    pattern_prompt = r"^\S+?#"
    pattern_more = r"^Press any key to continue.*$"
    pattern_syntax_error = r"Error: Bad command\.|Error: Invalid parameter\."
    command_disable_pager = "environment no more"
    command_exit = "logout"
    config_volatile = [r"^# Finished.*$", r"^# Generated.*$"]
    command_more = " "
    rogue_chars = [re.compile(rb"\r\s+\r"), b"\r"]
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "#", "end_of_context": "exit", "string_quote": '"'}

    rx_port_name = re.compile(r"(\d+\/\d+\/\d+)")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("0/1/1")
        'port0/1/1'
        """
        if self.rx_port_name.match(s):
            return "port%s" % s
        if "," in s:
            s = s.split(",", 1)[0].strip()
        return s

    INTERFACE_TYPES = {
        "port": "physical",
        "lag-": "aggregated",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:4].lower())
