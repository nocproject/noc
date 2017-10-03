# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: BDCOM
# OS:     xPON
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "BDCOM.xPON"
    pattern_username = r"Username: "
    pattern_password = r"Password: "
    pattern_more = [
        (r"^ --More-- ", " "),
        (r"\(y/n\) \[n\]", "y\n")
    ]
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)>"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    pattern_syntax_error = r"% Unknown command"
    command_more = " "
    command_disable_pager = ["terminal length 0", "terminal width 0"]
    command_super = "enable"
    command_enter_config = "config"
    command_leave_config = "exit"
    command_save_config = "write"
    command_exit = "exit"
    config_volatile = ["^%.*?$"]

    def convert_interface_name(self, interface):
        if interface.startswith("g"):
            return "GigaEthernet" + interface[1:]
        elif interface.startswith("epon"):
            return "EPON" + interface[4:]
        else:
            return interface
