# ---------------------------------------------------------------------
# Vendor: Nortel
# OS:     BayStack 425
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Nortel.BayStack425"

    pattern_username = rb"Enter Username:"
    pattern_password = rb"Enter Password:"
    pattern_prompt = rb"^\S+?#"
    pattern_more = [
        (rb"^----More", b" "),
        (rb"ommand Line Interface...", b"C"),
        (rb"Enter Ctrl-Y to begin", b"\x19"),
    ]
