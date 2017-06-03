# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     DSLAM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.DSLAM"
    pattern_username = r"(?<!Last )login: "
    pattern_more = [
        (r"--More-- ", " "),
        (r"\[Yes/press any key for no\]", "Y")
    ]
    pattern_prompt = r"(?P<hostname>\S+)> "
    pattern_syntax_error = r"Command not found"
#    command_disable_pager = "terminal datadump"
#    command_super = "enable"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"

    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"
