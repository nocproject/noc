# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QSW8200
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.QSW8200"

    pattern_more = [(rb"^ --More-- $", b" ")]
    pattern_unprivileged_prompt = rb"^\S+>"
    pattern_prompt = rb"^(?P<hostname>\S+)?#"
    pattern_syntax_error = rb"Error input in the position marke[td] by|%  Incomplete command"
    # Do not use this. Bogus hardware.
    # command_disable_pager = "terminal page-break disable"
    command_super = b"enable"
    command_submit = b"\r"
    command_exit = "quit"

    INTERFACE_TYPES = {
        "fa": "physical",  # fastethernet1/0/1
        "gi": "physical",  # gigaethernet1/1/7
        "te": "physical",  # tengigabitethernet1/1/28
        "tr": "aggregated",
        "vl": "SVI",  # vlan
        "lo": "loopback",  # loopback
        "un": "unknown",  # unknown
        "nu": "null",  # NULL
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2].lower())
