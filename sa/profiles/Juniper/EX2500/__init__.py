# -*- coding: utf-8 -*-
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
    pattern_more = [
        (r"^--More--", " "),
        (r"^Sure you want to close this session", "y\n")
    ]
    command_super = "enable"
    # command_enter_config = "configure terminal"
    # command_leave_config = "exit"
    pattern_unpriveleged_prompt = r"(?P<hostname>\S+?> )"
    pattern_prompt = r"(?P<hostname>\S+?# )"
    command_exit = "exit\nexit"

    rogue_chars = [
        "\r",
        re.compile(r"\n\n.*?\n"),
        re.compile(r"\n.*?:TELNET-ALERT:.*?\nvia TELNET/SSH From host .*?\n")
    ]
