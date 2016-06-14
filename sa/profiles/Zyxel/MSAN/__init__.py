# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zyxel
## OS:     MSAN
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.MSAN"
    pattern_prompt = r"^\S+?>"
    pattern_syntax_error = "invalid (command|input)"
    pattern_more = "Press any key to continue, 'n' to nopause,'e' to exit"
    config_volatile = [r"^time\s+(\d+|date).*?^"]
    command_more = "n"
    command_exit = "exit"
