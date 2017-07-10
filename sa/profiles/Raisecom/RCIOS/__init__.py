# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Raisecom
# OS:     RCIOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Raisecom.RCIOS"
    pattern_username = r"^([Uu]ser ?[Nn]ame|[Ll]ogin): ?"
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)> "
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>\S+)# "
    command_exit = "exit"
    pattern_syntax_error = r"% \".+\"  (?:Unknown command.)"

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

    def setup_script(self, script):
        if script.parent is None:
            s_password = script.credentials.get("super_password", "")
            self.pattern_more = [
                (r"^--More-- \(\d+% of \d+ bytes\)", "r"),
                (r"^Enable: ", s_password + "\n")
            ]

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())
