# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Polygon
# OS:     IOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Polygon.IOS"
    pattern_more = [
        (r"^ --More--", "\n"),
        (r"(?:\?|interfaces)\s*\[confirm\]", "\n")
    ]
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[-_\d\w]+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco
    config_volatile = ["^ntp clock-period .*?^"]

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
