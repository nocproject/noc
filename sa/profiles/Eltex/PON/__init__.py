# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Eltex
## OS:     PON
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## NOC modules
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.script import script


class Profile(NOCProfile):
    name = "Eltex.PON"
    pattern_username = r"^Login:"
    pattern_password = r"^Password:"
    pattern_more = [
        (r"\[Yes/press any key for no\]", "Y")
        ]
    pattern_unpriveleged_prompt = r"^\S+>"
    pattern_syntax_error = \
        r"^(Command not found. Use '?' to view available commands|" + \
        "Incomplete command\s+|Invalid argument\s+)"
#    command_disable_pager = "terminal datadump"
#    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"
    pattern_prompt = r"^\S+#"
#    convert_interface_name = NOCProfile.convert_interface_name_cisco

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
