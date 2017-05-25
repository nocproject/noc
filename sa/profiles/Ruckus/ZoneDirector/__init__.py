# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Ruckus
# OS:     ZoneDirector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''

from noc.core.profile.base import BaseProfile
import re


class Profile(BaseProfile):
    name = "Ruckus.ZoneDirector"
    pattern_more = [
        (r"^Login as:$", "\n"),
    ]
    pattern_username = "^[Pp]lease [Ll]ogin:"
    pattern_password = "^[Pp]assword:"
    pattern_unpriveleged_prompt = r"^\S*>"
    pattern_prompt = r"^\S*#"
    command_more = "\n"
    command_submit = "\n"
    command_super = "enable force"
    command_leave_config = "end"
    command_exit = "exit"
