# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     PON
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.PON"

    pattern_username = rb"(?<!Last) login: "
    pattern_more = [(rb"\[Yes/press any key for no\]", b"Y")]
    pattern_unprivileged_prompt = rb"^\S+>"
    pattern_syntax_error = rb"^(Command not found. Use '?' to view available commands|Incomplete command\s+|Invalid argument\s+)"
    #    command_disable_pager = "terminal datadump"
    #    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"
    pattern_prompt = rb"^\S+#"
    #    convert_interface_name = BaseProfile.convert_interface_name_cisco

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
                self.script.cli("exit\r")
