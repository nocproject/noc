# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: DCN
# OS:     DCWS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''

from noc.core.profile.base import BaseProfile
import re

class Profile(BaseProfile):
    name = "DCN.DCWS"
    pattern_more = [
        (r"^ --More-- ", "\n")
    ]
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    command_more = "\n"
    command_submit = "\n"
    command_exit = "exit"
