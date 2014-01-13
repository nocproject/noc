# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     SCOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Cisco.SCOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = [
        (r"--More--", " "),
        (r"\?\s*\[confirm\]", "\n")
    ]
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% invalid input |% Ambiguous command:|% Incomplete command."
#    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9]\S*?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = NOCProfile.convert_mac_to_cisco

    def convert_interface_name(self, interface):
        if interface.startswith("Fast"):
            return "Fa " + interface[12:].strip()
        elif interface.startswith("Giga"): 
            return "Gi " + interface[15:].strip()
        elif interface.startswith("Ten"):
            return "Te " + interface[18:].strip()
        else:
            return interface
