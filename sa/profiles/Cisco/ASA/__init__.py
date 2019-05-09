# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     ASA
# Compatible: 7.0
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.ASA"
    pattern_more = "^<--- More --->"
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    pattern_username = r"^\s*([Uu]ser ?[Nn]ame|[Ll]ogin): ?"  # Fix for exclude "...Last login: 10:48:33 MS..." match
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "logout"
    pattern_prompt = r"^\S+?#"
    command_more = " "
    command_disable_pager = "terminal pager 0"
    default_parser = "noc.cm.parsers.Cisco.ASA.base.BaseASAParser"
    config_volatile = [r"\sat\s\d+:\d+:\d+\.\d+\s\S+\s\S+\s\S+\s\d+\s\d+\n"]

    def convert_interface_name(self, interface):
        il = interface.lower()
        if il.startswith("mgmt"):
            return "Mg " + interface[4:]
        return self.convert_interface_name_cisco(interface)

    INTERFACE_TYPES = {
        "L": "loopback",
        "I": "loopback",
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
