# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     LTE
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.LTE"
    pattern_username = r"(?<!Last )login: "
    pattern_more = [(r"\[Yes/press any key for no\]", "Y")]
    # pattern_unprivileged_prompt = r"^\S+>"
    pattern_syntax_error = r"^(Command not found|Incomplete command|Invalid argument)"
    pattern_operation_error = r"Data verify failed, bad MAC!"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"
    pattern_prompt = r"^\S+[#>]"

    class switch(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter switch context"""
            self.script.cli("switch")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                self.script.cli("exit")
