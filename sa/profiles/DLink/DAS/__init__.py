# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: D-Link
# OS:     DAS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DAS"
    pattern_syntax_error = r"(Error: Invalid command)"
    pattern_prompt = r"(?P<hostname>\S*)[#$]"
    command_exit = "logout"
    config_volatile = ["^%.*?$"]
    telnet_naws = "\x00\x7f\x00\x7f"
