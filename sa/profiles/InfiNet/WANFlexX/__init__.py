# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: InfiNet
# OS:     WANFlexX
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "InfiNet.WANFlexX"
    pattern_more = [(r"^-- more --$", " ")]
    pattern_prompt = r"(?P<hostname>\S+?)#\d+>"
    command_submit = "\r"
    username_submit = "\r"
    password_submit = "\r"
    command_exit = "exit"
    pattern_syntax_error = r"Unknown command\. Use \? for help"
