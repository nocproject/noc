# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Nateks
# OS:     FlexFain ACE 8/16
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Nateks.FlexGainACE16"
    pattern_more = [
        (r"^logged on; type `exit' to close connection.", "\n"),
        (r"^Press 'y' to continue, 'n' to break and press Enter", "\n"),
        (r"^Yes or No <y/n>", "y\n")
    ]
    pattern_syntax_error = r"% Unknown action |% Ambiguous command:"
    pattern_username = "user:"
    pattern_password = "[Pp]assword:"
    command_submit = "\n"

    pattern_prompt = r"^IPDSLAM#"
    command_exit = "exit"
    command_save_config = "commit\n"
