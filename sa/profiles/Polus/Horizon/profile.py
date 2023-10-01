# ---------------------------------------------------------------------
# Vendor: Polus
# OS:     Horizon
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Polus.Horizon"

    http_request_middleware = [
        "noc.sa.profiles.Polus.Horizon.middleware.horizonauth.HorizonAuthMiddeware",
    ]

    pattern_prompt = rb"(.+):>"
    command_exit = b"quit"
    rogue_chars = [b"\r", b"\\x1b", re.compile(rb"\[\d+;\d+m")]
