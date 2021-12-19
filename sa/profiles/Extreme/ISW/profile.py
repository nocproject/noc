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

    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_prompt = rb"^(?P<hostname>\S+)#"
    pattern_syntax_error = rb"% (Incomplete command|Invalid (input|word) detected at)"
    pattern_more = [(rb"^-- more --, next page: Space, continue: g, quit: \^C", b"g")]
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
