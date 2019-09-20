# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Alstec (www.alstec.ru)
# OS:     ALS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alstec.ALS"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"% Unrecognized command|% Wrong number of parameters"
    command_super = "enable"
    command_disable_pager = "terminal datadump"
    pattern_more = "More: <space>,  Quit: q or CTRL+Z, One line: <return>"
    command_more = "a"

    INTERFACE_TYPES = {
        "e": "physical",  # Ethernet
        "g": "physical",  # GigabitEthernet
        "t": "physical",  # TenGigabitEthernet
        "p": "aggregated",  # Port-channel/Portgroup
        "c": "aggregated",  # ch
        "v": "SVI",  # vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:1].lower())
