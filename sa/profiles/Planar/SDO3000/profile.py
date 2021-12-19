# ----------------------------------------------------------------------
# Vendor: Planar
# OS:     SDO3000
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Planar.SDO3000"

    pattern_username = rb"Login: "
    pattern_password = rb"Password: "
    pattern_prompt = rb"Select:"
    pattern_more = [(rb"^Press <Enter> to continue or <Esc> to cancel\.", b"\n")]
    username_submit = b"\r\n"
    password_submit = b"\r\n"
    command_exit = "0"
    rogue_chars = [b"\r", re.compile(br"(\x1b\[\S\S)+(;1H)?")]
