# ---------------------------------------------------------------------
# Vendor: Symbol
# OS:     AP
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Symbol.AP"

    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>"
    pattern_prompt = rb"^(?P<hostname>\S+)#"
    pattern_syntax_error = rb"% Invalid input detected at"
    pattern_more = [(rb"--More-- ", b" ")]
    command_super = b"enable"

    INTERFACE_TYPES = {
        "ge": "physical",
        "vl": "SVI",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
