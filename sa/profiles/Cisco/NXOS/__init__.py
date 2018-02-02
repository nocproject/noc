# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     NX-OS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.NXOS"
    pattern_more = "^--More--"
    pattern_unprivileged_prompt = r"^\S+?>"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = r"^\S+?#"
    pattern_syntax_error = r"% Invalid command at"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco

    def convert_interface_name(self, interface):
        return self.convert_interface_name_cisco(interface)

    INTERFACE_TYPES = {
        "Et": "physical",  # Ethernet
        "mg": "management",
        "Mg": "management",
        "Po": "aggregated",  # Port-channel/Portgroup
        "po": "aggregated",  # Port-channel/Portgroup
        "vf": "aggregated",  # FCoE FiberChannel Over Ethernet
        "Vl": "SVI"  # Vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
