# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Iskratel
# OS:     ESCOM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.ESCOM"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"% Unrecognized command|% Wrong number of parameters"
    command_super = "enable"
    command_disable_pager = "terminal datadump"
    pattern_more = "More: <space>,  Quit: q or CTRL+Z, One line: <return>"
    command_more = "a"

    convert_interface_name = BaseProfile.convert_interface_name_cisco

    INTERFACE_TYPES = {
        "oo": "management",
        "fa": "physical",  # FastEthernet
        "gi": "physical",  # gigabitethernet
        "te": "physical",  # gigabitethernet
        "Lo": "loopback",  # Loopback
        "Po": "aggregated",  # Port-channel/Portgroup
        "vl": "SVI",  # vlan
        "Vl": "SVI",  # Vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
