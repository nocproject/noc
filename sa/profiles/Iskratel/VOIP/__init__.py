# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Iskratel
# OS:     VOIP
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.VOIP"
    # Iskratel do not have "enable_super" command
    # pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_prompt = r"^=>"
    pattern_more = r"^Press any key to continue or Esc to stop scrolling."
    pattern_syntax_error = r"Syntax error|Command line error|Illegal command name"
    command_more = " "
    command_exit = "exit"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    command_submit = "\r\n"
    rogue_chars = ["\r\x00"]
