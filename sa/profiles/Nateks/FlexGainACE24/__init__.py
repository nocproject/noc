# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Nateks
# OS:     FlexFain
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
Test in FlexGain ACE24 DSLAM
"""

from noc.core.profile.base import BaseProfile
import re


class Profile(BaseProfile):
    name = "Nateks.FlexGainACE24"
    pattern_more = [
       (r"^Login Successful------", "\n\r")
    ]
    pattern_syntax_error = r"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    pattern_username = "[Ll]ogin:"
    pattern_password = "[Pp]assword:"

    pattern_prompt = r"(^\$\s+|^>\s)"
#    pattern_unpriveleged_prompt = r"$\s"
    command_exit = "exit"
    command_save_config = "commit\n"
