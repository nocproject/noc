# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: DCN
# OS:     DCWL
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DCN.DCWL"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#|~ #"
    command_more = "\n"
    command_submit = "\n"
    command_exit = "exit"

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

    INTERFACE_TYPES = {

        "lo": "loopback",  # Loopback

    }

    INTERFACE_TYPES2 = {

        "brv": "unknown",  # No comment
        "eth": "physical",  # No comment
        "wla": "physical",  # No comment

    }

    @classmethod
    def get_interface_type(cls, name):
        c = cls.INTERFACE_TYPES2.get(name[:3])
        if c:
            return c
        c = cls.INTERFACE_TYPES.get(name[:2])
        return c
