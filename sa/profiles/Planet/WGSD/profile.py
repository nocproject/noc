# ---------------------------------------------------------------------
# Vendor: Planet
# OS:     WGSD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.validators import is_int


class Profile(BaseProfile):
    name = "Planet.WGSD"

    pattern_more = [
        (rb"^More: <space>,  Quit: q, One line: <return>$", b" "),
        (rb"\[Yes/press any key for no\]", b"Y"),
        (rb"<return>, Quit: q or <ctrl>", b" "),
        (rb"q or <ctrl>+z", b" "),
    ]
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>\s*"
    pattern_syntax_error = (
        rb"^% (Unrecognized command|Incomplete command|"
        rb"Wrong number of parameters or invalid range, size or "
        rb"characters entered)$"
    )
    command_disable_pager = "terminal datadump"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = rb"^(?P<hostname>[A-Za-z0-9-_ \:\.\*\'\,\(\)\/]+)#"

    INTERFACE_TYPES = {
        "e": "physical",  # Ethernet
        "g": "physical",  # GigabitEthernet
        "c": "aggregated",  # Port-channel/Portgroup
        "v": "SVI",  # VLAN,
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:1]).lower())

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("19")
        'vlan 19'
        """
        if is_int(s):
            return "vlan %s" % s
        return s
