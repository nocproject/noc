# -*- coding: utf-8 -*-
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
    pattern_username = r"Login: "
    pattern_password = r"Password: "
    pattern_prompt = r"Select:"
    pattern_more = [(r"^Press <Enter> to continue or <Esc> to cancel\.", "\n")]
    username_submit = "\r\n"
    password_submit = "\r\n"
    command_exit = "0"
    rogue_chars = ["\r", re.compile(r"(\x1b\[\S\S)+(;1H)?")]
