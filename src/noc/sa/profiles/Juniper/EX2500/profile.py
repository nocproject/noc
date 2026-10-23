# ----------------------------------------------------------------------
# Vendor: Juniper
# OS:     EX2500
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Juniper.EX2500"
    pattern_more = [(rb"^--More--", b" "), (rb"^Sure you want to close this session", b"y\n")]
    command_super = b"enable"
    # command_enter_config = "configure terminal"
    # command_leave_config = "exit"
    pattern_unpriveleged_prompt = rb"(?P<hostname>\S+?> )"
    pattern_prompt = rb"(?P<hostname>\S+?# )"
    command_exit = "exit\nexit"

    rogue_chars = [
        b"\r",
        re.compile(rb"\n\n.*?\n"),
        re.compile(rb"\n.*?:TELNET-ALERT:.*?\nvia TELNET/SSH From host .*?\n"),
    ]
