# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: BDCOM
# OS:     IOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "BDCOM.IOS"
    pattern_more = [
        (r"^ --More-- ", " "),
        (r"\(y/n\) \[n\]", "y\n")
    ]
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)>"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    pattern_syntax_error = r"^Unknown command"
    command_disable_pager = ["terminal length 0", "terminal width 0"]
    command_super = "enable"
    command_enter_config = "config"
    command_leave_config = "exit"
    command_save_config = "write"
    command_exit = "exit"
    config_volatile = ["^%.*?$",
                       r"enable password 7 \S+( level \d+)?\n",
                       r"username \S+ password 7 \S+( author\-group \S+)?\n"]

    def convert_interface_name(self, interface):
        if interface.startswith("f"):
            return interface.replace("f", "FastEthernet")
        elif interface.startswith("g"):
            return interface.replace("g", "GigaEthernet")
        elif interface.startswith("v"):
            return interface.replace("v", "VLAN")
        elif interface.startswith("n"):
            return interface.replace("n", "Null")
        else:
            return interface
