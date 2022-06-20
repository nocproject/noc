# ----------------------------------------------------------------------
# Vendor: 3Com
# OS:     SuperStack3_4500
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "3Com.SuperStack3_4500"
    pattern_more = [
        (rb"^ +---- More ----$", b" "),
        (rb"The current configuration will be written to the device. Are you sure? [Y/N]:", b"Y"),
        (rb"(To leave the existing filename unchanged, press the enter key):", b"\n"),
        (rb"flash:/startup.cfg exists, overwrite? [Y/N]:", b"Y"),
    ]
    pattern_prompt = rb"^[<\[]\S+[>\]]"
    pattern_syntax_error = rb"\s+% (?:Unrecognized|Incomplete) command found at '\^' position."
    rogue_chars = [re.compile(rb"\x1b\[42D\s+\x1b\[42D"), b"\r"]
    command_save_config = "save"
    command_enter_config = "system-view"
    command_leave_config = "return"
    command_exit = "quit"
    convert_interface_name = BaseProfile.convert_interface_name_cisco

    INTERFACE_TYPES = {
        "Et": "physical",  # Ethernet
        "Gi": "physical",  # GigabitEthernet
        "Po": "aggregated",  # Aggregated
        "Lo": "loopback",  # LoopBack
        "NU": "null",  # NULL
        "Vl": "SVI",  # Vlan-interface
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
