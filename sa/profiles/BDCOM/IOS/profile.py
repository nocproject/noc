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

    pattern_more = [(rb"^ --More-- ", b" "), (rb"\(y/n\) \[n\]", b"y\n")]
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>"
    pattern_prompt = rb"^(?P<hostname>\S+)#"
    pattern_syntax_error = rb"^Unknown command"
    command_disable_pager = ["terminal length 0", "terminal width 0"]
    command_super = b"enable"
    command_enter_config = "config"
    command_leave_config = "exit"
    command_save_config = "write"
    command_exit = "exit"
    config_volatile = [
        "^%.*?$",
        r"enable password 7 \S+( level \d+)?\n",
        r"username \S+ password 7 \S+( author\-group \S+)?\n",
    ]

    def convert_interface_name(self, interface):
        if interface.startswith("TGigaEthernet"):
            return interface
        elif interface.startswith("GigaEthernet"):
            return interface

        if interface.startswith("f"):
            return interface.replace("f", "FastEthernet")
        elif interface.startswith("g"):
            return interface.replace("g", "GigaEthernet")
        elif interface.startswith("Gig"):
            return interface.replace("Gig", "GigaEthernet")
        elif interface.startswith("TGi"):
            return interface.replace("TGi", "TGigaEthernet")
        elif interface.startswith("tg"):
            return interface.replace("tg", "TGigaEthernet")
        elif interface.startswith("v"):
            return interface.replace("v", "VLAN")
        elif interface.startswith("n"):
            return interface.replace("n", "Null")
        else:
            return interface
