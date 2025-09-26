# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     WOP
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.WOP"

    pattern_prompt = rb"^(?P<hostname>\S+)\s*#|~ #"
    command_more = b"\n"
    command_submit = b"\n"
    command_exit = "exit"
    pattern_syntax_error = rb"Invalid command\."

    INTERFACE_TYPES = {
        "lo": "loopback",  # Loopback
        "brv": "SVI",  # No comment
        "brt": "SVI",
        "isa": "unknown",
        "eth": "physical",  # No comment
        "wla": "physical",  # No comment
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:3])

    @staticmethod
    def table_parser(v):
        """
        Parse table
        :param v:
        :return:
        """
        r = {}
        for line in v.splitlines():
            if not line.strip(" -"):
                continue
            value = line.split(" ", 1)
            if len(value) == 2:
                r[value[0].strip()] = value[1].strip()
            else:
                r[value[0]] = None
        return r
