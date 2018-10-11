# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Rotek
# OS:     RTBSv1
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Rotek.RTBSv1"
    pattern_prompt = r"^(?P<hostname>\S+)\s*>?|\W+?#\s+?"
    pattern_syntax_error = r"(ERROR|show: not found)"
    command_submit = "\r"
    enable_cli_session = False
    command_exit = "exit\rlogout"
    INTERFACE_TYPES = {
        "et": "physical",
        "lo": "loopback",
        "tu": "tunnel",
        "br": "physical",
        "at": "physical",
        "wi": "physical"
    }

    @classmethod
    def get_interface_type(cls, name):
        if name is None:
            return None
        return cls.INTERFACE_TYPES.get(name[:2])

    class shell(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter switch context"""
            raise NotImplementedError("Not supported work on Shell")
            # self.script.cli("shell")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                self.script.cli("\r")

    matchers = {
        "is_platform_BS5": {
            "platform": {
                "$regex": r"^RT-BS5"
            }
        },
        "is_platform_BS24": {
            "platform": {
                "$regex": r"^RT-BS24"
            }
        }
    }
