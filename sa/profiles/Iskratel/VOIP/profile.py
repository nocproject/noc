# ---------------------------------------------------------------------
# Vendor: Iskratel
# OS:     VOIP
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.VOIP"

    # Iskratel do not have "enable_super" command
    # pattern_unprivileged_prompt = r"^\S+?>"
    pattern_username = rb"^user id :"
    pattern_prompt = rb"^=>"
    pattern_more = rb"^Press any key to continue or Esc to stop scrolling."
    pattern_syntax_error = rb"Syntax error|Command line error|Illegal command name"
    command_more = " "
    command_exit = "exit"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    command_submit = b"\r\n"
    rogue_chars = [b"\r\x00"]
