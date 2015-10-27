# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     NX-OS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.NXOS"
    pattern_more = "^--More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = r"^\S+?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco

    def convert_interface_name(self, interface):
        il = interface.lower()
        if il.startswith("ethernet"):
            return "Eth" + interface[8:]
        else:
            return interface
