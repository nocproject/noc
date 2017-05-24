# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Maipu
# OS:     OS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile
import re



class Profile(BaseProfile):
    name = "Maipu.OS"
    pattern_more = [
        (r"^....press ENTER to next line, Q to quit, other key to next page....", "\n"),
        (r"Startup config in flash will be updated, are you sure", "y"),
    ]

    command_exit = "quit"
    command_super = "enable"
    command_enter_config = "configure t"
    command_leave_config = "end"
    command_save_config = "save"
    
    pattern_syntax_error = r"% Unrecognized command, and error detected at \'^\' marker."
    pattern_unpriveleged_prompt = r"^(?P<hostname>[a-zA-Z0-9-_\.]+)(?:-[a-zA-Z0-9/]+)*>$"
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9-_\.]+)(?:-[a-zA-Z0-9/]+)(\(config\))*[*\)>#]$"

