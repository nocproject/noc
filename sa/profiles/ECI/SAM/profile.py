# ----------------------------------------------------------------------
# Vendor: ECI http://www.ecitele.com/
# OS:     SAM
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ECI.SAM"

    pattern_username = rb"^[Ll]ogin :"
    pattern_password = rb"^[Pp]assword :"
    username_submit = b"\r\n"
    password_submit = b"\r\n"
    command_submit = b"\r\n"
    pattern_prompt = rb"^( >>|\S+ >(?: \S+ >)?|\S+ (?:\- SHOW(?:\\\S+)?)?>)"
    pattern_syntax_error = rb": no such command"

    # pattern_prompt = r"^Select menu option.*:"
    pattern_more = [
        (rb"Enter <CR> for more or 'q' to quit--:", b"\r"),
        (rb"press <SPACE> to continue or <ENTER> to quit", b"               \n"),
    ]
    command_exit = "logout"
    # telnet_slow_send_password = True
    # telnet_send_on_connect = "\r"
    # convert_mac = BaseProfile.convert_mac_to_dashed

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
        "cp": "physical",  # FortyGigabitEthernet
        "sw": "SVI",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())
