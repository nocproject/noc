# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     ASA
## Compatible: 7.0
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.ASA"
    pattern_more = "^<--- More --->"
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^\S+?#"
    command_more = " "
    command_disable_pager = "terminal pager 0"

    def convert_interface_name(self, interface):
        il = interface.lower()
        if il.startswith("mgmt"):
            return "Mg " + interface[4:]
        return self.convert_interface_name_cisco(interface)

    INTERFACE_TYPES = {
            "L": "loopback",
            "E": "physical",
            "G": "physical",
            "T": "physical",
            "M": "management",
            "R": "aggregated",
            "P": "aggregated",
            "V": "SVI"
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[0])
