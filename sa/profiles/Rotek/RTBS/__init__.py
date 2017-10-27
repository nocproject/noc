# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Rotek
# OS:     RTBS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Rotek.RTBS"
    pattern_prompt = r"^(?P<hostname>\S+)\s*>?|\W+?#\s+?"
    pattern_syntax_error = r"^\(ERROR\)"
    command_submit = "\r"
    command_exit = "logout"

    INTERFACE_TYPES = {
        "et": "physical",
        "lo": "loopback",
        "tu": "tunnel",
        "gr": "tunnel",
        "br": "physical",
        "ra": "physical"
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])

    class shell(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter switch context"""
            self.script.cli("shell")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                self.script.cli("exit\r")
