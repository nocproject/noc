# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Zhone
# OS:     MXK
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zhone.MXK"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"ERROR: Permission denied."
    pattern_more = \
        "<SPACE> for next page, <CR> for next line, A for all, Q to quit"
    command_more = "a"
