# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: OneAccess
# OS:     TDRE
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "OneAccess.TDRE"
    pattern_more = "^--More--"
    pattern_prompt = r"^\S*>"
    command_more = " "
    command_exit = "DISCONNECT"
    command_submit = "\r\n"
    username_submit = "\r"
    password_submit = "\r"
    rogue_chars = [
        re.compile(
            r"Login successful -- CLI active -- connecting with device\r\n>"
        ), "\r"
    ]
