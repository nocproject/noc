# -*- coding: utf-8 -*-
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
    name = "Nateks.netxpert"
    pattern_more = [
        (r"^ --More-- ", "\n"),
        (r"(?:\?|interfaces)\s*\[confirm\]", "\n")
    ]
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = \
        r"% Invalid input detected at|% Ambiguous command:|" \
        r"% Incomplete command."
    command_super = "enable"
    command_leave_config = "exit"
    command_exit = "exit"
    command_save_config = "write\n"
    pattern_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9/.]\S{0,35})(?:[-_\d\w]+)?" \
        r"(?:\(_config[^\)]*\))?#"
