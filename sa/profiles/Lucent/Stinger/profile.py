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

    pattern_syntax_error = rb"(error: shelf: unknown value)"
    pattern_username = rb"User:\s*"
    pattern_password = rb"Password:\s*"
    pattern_prompt = rb"(?P<hostname>\S+)>"
    command_exit = "quit"
