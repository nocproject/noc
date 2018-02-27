# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Iskratel
# OS:     MBAN
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.MBAN"
    # Iskratel do not have "enable_super" command
    # pattern_unprivileged_prompt = r"^\S+?>"
    pattern_username = r"^user id :"
    pattern_prompt = r"^\S+?>"
    pattern_more = [
        (r"^Press any key to continue or Esc to stop scrolling.\r\n", " "),
        (r"^Press any key to continue", " ")  # Need more examples
    ]
    # pattern_more = "^Press any key to continue or Esc to stop scrolling.\r\n"
    pattern_syntax_error = r"Illegal command name"
    command_more = " "
    command_exit = "exit"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    enable_cli_session = False
    command_submit = "\r\n"
    rogue_chars = ["\r\x00"]
