# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Extreme
# OS:     ISW
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Extreme.ISW"
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    pattern_syntax_error = r"% (Incomplete command|Invalid (input|word) detected at)"
    pattern_more = [(r"^-- more --, next page: Space, continue: g, quit: \^C", "g")]
    command_exit = "exit"
    convert_interface_name = BaseProfile.convert_interface_name_cisco

    INTERFACE_TYPES = {
        "Fa": "physical",  # FastEthernet
        "Gi": "physical",  # GigabitEthernet
        "VL": "SVI",  # VLAN, found on C3500XL
        "Vl": "SVI",  # Vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
