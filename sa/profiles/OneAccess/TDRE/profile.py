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

    pattern_more = [(rb"^--More--", b" ")]
    pattern_prompt = rb"^\S*>"
    command_exit = "DISCONNECT"
    command_submit = b"\r\n"
    username_submit = b"\r"
    password_submit = b"\r"
    rogue_chars = [
        re.compile(b"Login successful -- CLI active -- connecting with device\r\n>"),
        b"\r",
    ]
