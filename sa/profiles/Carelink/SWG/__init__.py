# -*- coding: utf-8 -*-
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
    pattern_username = r"(?<!Login in progress\.\.\.)Username: "
    pattern_prompt = r"^(\S+)# "
    pattern_more = r"^---More---\n"
    pattern_syntax_error = r"\n(Invalid command|\*Incomplete command)"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    command_exit = "quit"
