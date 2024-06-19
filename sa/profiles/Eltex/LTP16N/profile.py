# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     LTP-16N
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.LTP16N"

    # pattern_username = rb"(?<!Last>)([Uu]ser ?[Nn]ame|[Ll]ogin): ?"
    pattern_username = rb"(.+ login:)(\s+$)"
    # pattern_more = [(rb"--More--\([0-9]+%\)", b"\r\n"), (rb"\[Yes/press any key for no\]", b"Y")]
    pattern_more = [(rb"--More--\([0-9]+%\)", b" "), (rb"\[Yes/press any key for no\]", b"Y")]
    pattern_unprivileged_prompt = rb"^\S+>"
    pattern_syntax_error = (
        rb"(Command not found. Use '?' to view available commands|"
        rb"Incomplete command\s+|Invalid argument\s+|Unknown command)"
    )

    #    command_disable_pager = "terminal datadump"
    #    command_super = "enable"
    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"

    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"
    pattern_prompt = rb"^\S+#"

    PLATFORMS = {
        "209": {
            "platform": "LTP-16N",
            "HW": "1.3.6.1.4.1.35265.1.209.1.1.2.0",
            "SW": "1.3.6.1.4.1.35265.1.209.1.1.3.0",
            "SN": "1.3.6.1.4.1.35265.1.209.2.3.1.4.0",
        },
        "297": {
            "platform": "LTP-8N",
            "HW": "1.3.6.1.4.1.35265.1.209.1.1.2.0",
            "SW": "1.3.6.1.4.1.35265.1.209.1.1.3.0",
            "SN": "1.3.6.1.4.1.35265.1.209.2.3.1.4.0",
        },
    }

    matchers = {
        "is_LTP16N": {"platform": {"$regex": r"LTP-16N"}},
    }

    def get_platform(self, s):
        return self.PLATFORMS.get(s)

    class switch(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter switch context"""
            self.script.cli("switch")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                self.script.cli("exit\r")

    rx_interface_name = re.compile(r"^(?P<ifname>\S.+)\s+(?P<number>\d+)", re.MULTILINE)

    def convert_interface_name(self, s):
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        if "PON channel" in match.group("ifname"):
            return "pon-port %s" % match.group("number")
        elif "Uplink" in match.group("ifname") and int(match.group("number")) <= 7:
            return "front-port %s" % match.group("number")
        elif "Uplink" in match.group("ifname") and int(match.group("number")) > 7:
            return "10G-front-port %s" % (int(match.group("number")) - 8)
        else:
            return s

    def get_count_pon_ports(self):
        return 16 if self.is_LTP16N else 8
