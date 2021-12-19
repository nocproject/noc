# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     LTE
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.LTE"

    pattern_username = rb"(?<!Last )login: "
    pattern_more = [(rb"\[Yes/press any key for no\]", b"Y")]
    # pattern_unprivileged_prompt = r"^\S+>"
    pattern_syntax_error = rb"\n(Command not found|Incomplete command|Invalid argument)"
    pattern_operation_error = rb"Data verify failed, bad MAC!"
    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"
    pattern_prompt = rb"^\S+[#>]"

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
