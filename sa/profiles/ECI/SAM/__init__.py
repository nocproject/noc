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
    pattern_username = r"^Login :"
    pattern_password = r"^Password :"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    pattern_prompt = r"^(?P<hostname>\S+) (?:\- SHOW(?:\\\S+)?)?>"

    #pattern_prompt = r"^Select menu option.*:"
    pattern_more = [
        (r"Enter <CR> for more or 'q' to quit--:", "\r"),
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

    def setup_session(self, script):
        script.cli("SHOW")
