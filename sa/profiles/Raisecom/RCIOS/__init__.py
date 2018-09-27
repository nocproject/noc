# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Raisecom
# OS:     RCIOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Raisecom.RCIOS"
    pattern_username = r"^([Uu]ser ?[Nn]ame|[Ll]ogin): ?"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)> "
    pattern_super_password = r"^Enable: "
    cli_retries_super_password = 2
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>\S+)# "
    command_exit = "exit"
    pattern_syntax_error = r"% \".+\"  (?:Unknown command.)"
    pattern_more = [
        (r"^--More-- \(\d+% of \d+ bytes\)", "r")
    ]

    INTERFACE_TYPES = {
        "3g": "tunnel",
        "du": "other",
        "et": "physical",
        "lo": "loopback",
        "sh": "physical",
        "si": "physical",
        "tu": "tunnel",
        "vl": "SVI",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())
