# ---------------------------------------------------------------------
# Vendor: Nateks
# OS:     NetXpert
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
Test:
- NX-3408-DC
"""

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Nateks.NetXpert"

    pattern_more = [(rb"^ --More-- ", b"\n"), (rb"(?:\?|interfaces)\s*\[confirm\]", b"\n")]
    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_syntax_error = (
        rb"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    )
    command_super = b"enable"
    command_leave_config = "exit"
    command_exit = "exit"
    command_save_config = "write\n"
    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9/.]\S{0,35})(?:[-_\d\w]+)?(?:\(_config[^\)]*\))?#"
