# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: HP
## OS:     Comware
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.Comware"
    pattern_more = [(r"^.+---- More ----$", " ")]
    command_more = " "
    pattern_prompt = r"^[<\[]\S+[>\]]"
    command_exit = "quit"
    rogue_chars = [
        re.compile(r"                "),
        "\r"
    ]

