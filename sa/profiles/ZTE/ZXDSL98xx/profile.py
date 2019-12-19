# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: ZTE
# OS:     ZXDSL98xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXDSL98xx"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+>)"
    pattern_prompt = r"^(?!#)\S+[$#] "
    pattern_syntax_error = r"Error: (%Invalid parameter|Bad command)"
    pattern_operation_error = r"Error: Too many user login..."
    pattern_more = r"\nPress any key to continue \(Q to quit\)"
    # Are you sure to quit? yes[Y] or no[N]
    command_more = " "
    command_super = "enable"
    rogue_chars = [re.compile(r"^\s{10,}\r"), "\r"]
    config_volatile = ["<entry1 sessionID=.+?/>"]
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    command_exit = "logout"
    telnet_send_on_connect = "\n"

    matchers = {"is_9806h": {"platform": {"$regex": "9806H"}}}
