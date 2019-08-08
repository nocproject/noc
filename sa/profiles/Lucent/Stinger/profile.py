# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  Vendor: Lucent
#  OS:     Stinger
# ---------------------------------------------------------------------
#  Copyright (C) 2007-2016 The NOC Project
#  See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Lucent.Stinger"
    pattern_syntax_error = r"(error: shelf: unknown value)"
    pattern_username = r"User:\s*"
    pattern_password = r"Password:\s*"
    pattern_prompt = r"(?P<hostname>\S+)>"
    command_exit = "quit"
