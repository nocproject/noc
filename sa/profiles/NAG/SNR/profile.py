# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: NAG
# OS:     SNR
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NAG.SNR"
    pattern_more = [
        (r"^ --More-- ", "\n"),
        (r"^Confirm to overwrite current startup-config configuration \[Y/N\]:", "y\n"),
    ]
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    command_disable_pager = "terminal length 200"
    command_exit = "exit"
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}
