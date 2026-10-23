# ----------------------------------------------------------------------
# Vendor: Carelink
# OS:     SWG
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Carelink.SWG"

    pattern_username = rb"(?<!Login in progress\.\.\.)Username: "
    pattern_prompt = rb"^(\S+)# "
    pattern_more = [(rb"^---More---\n", b"\r")]
    pattern_syntax_error = rb"^(Invalid command|\*Incomplete command)"
    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"
    command_exit = "quit"
