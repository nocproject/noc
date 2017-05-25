# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT8700
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT8700"
    pattern_more = r"^--More--\s*\(<space> = next page, <CR> = one line, C = continuous, Q = quit\)"
    command_more = "c"
    command_submit = "\r"
    username_submit = "\r"
    command_save_config = "save configuration"
    # pattern_prompt = r"^(?P<hostname>[\S\s]+)>"
    pattern_prompt = r"^(Manager)\s*(?P<hostname>\S+)>"
    command_exit = "logout"
