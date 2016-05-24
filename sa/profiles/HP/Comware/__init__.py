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
    command_more = " "
    command_exit = "quit"
    pattern_more = [(r"^.+---- More ----$", " ")]
    pattern_prompt = r"^[<\[]\S+[>\]]"
    pattern_syntax_error = \
        r"% (?:Unrecognized command|Too many parameters|Incomplete command)" \
        r" found at"
    rogue_chars = [
        re.compile(r"                "),
        "\r"
    ]
