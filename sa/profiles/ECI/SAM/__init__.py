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
    pattern_syntax_error = r": no such command"

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

    INTERFACE_TYPES = {
        "lo": "loopback",  # Loopback
        "fe": "physical",  # FortyGigabitEthernet
        "vn": "physical",  # FortyGigabitEthernet
        "en": "physical",  # FortyGigabitEthernet
        "at": "physical",  # FortyGigabitEthernet
        "cp": "physical"  # FortyGigabitEthernet
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())
