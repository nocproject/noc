# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: ZTE
# OS:     ZXDSL98xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXDSL98xx"
    pattern_prompt = "^(?!#)\S+[$#] "
    pattern_syntax_error = r"Error: (%Invalid parameter|Bad command)"
    pattern_more = r"\nPress any key to continue \(Q to quit\)"
    command_more = " "
    rogue_chars = [re.compile(r"^\s{10,}\r"), "\r"]

    config_volatile = ["<entry1 sessionID=.+?/>"]
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    command_exit = "logout"
    # Error: Too many user login...
