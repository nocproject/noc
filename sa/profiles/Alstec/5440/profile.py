# ---------------------------------------------------------------------
# Vendor: Alstec
# OS:     5440
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alstec.5440"

    pattern_prompt = rb"^ > "
    pattern_syntax_error = rb"telnetd:error:"
    command_exit = "logout"
