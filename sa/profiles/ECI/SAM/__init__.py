# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: ECI http://www.ecitele.com/
# OS:     SAM
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ECI.SAM"
    pattern_username = r"^[Ll]ogin :"
    pattern_password = r"^[Pp]assword :"
    username_submit = "\r\n"
    password_submit = "\r\n"
    command_submit = "\r\n"
    pattern_prompt = r"^( >>|\S+ >(?: \S+ >)?|\S+ (?:\- SHOW(?:\\\S+)?)?>)"

    #pattern_prompt = r"^Select menu option.*:"
    pattern_more = [
        (r"Enter <CR> for more or 'q' to quit--:", "\r"),
        (r"press <SPACE> to continue or <ENTER> to quit", "               \n"),
    ]
    command_exit = "logout"
    #telnet_slow_send_password = True
    #telnet_send_on_connect = "\r"
    #convert_mac = BaseProfile.convert_mac_to_dashed

    def setup_script(self, script):
        if script.parent is None:
            user = script.credentials.get("user", "")
            # Add three random chars to begin of `user`
            # Do not remove this
            script.credentials["user"] = "   " + user

    class shell(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter switch context"""
            self.script.cli("SHOW")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                self.script.cli("END\r")
