# ---------------------------------------------------------------------
# Vendor: Zyxel
# OS:     ZyNOS_EE
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.ZyNOS_EE"

    pattern_password = b"Password: "
    pattern_prompt = rb"^\S+?> "
    pattern_more = [(rb"^-- more --.*?$", b" ")]
    pattern_syntax_error = rb"^Valid commands are:"
    command_exit = "exit"
    enable_cli_session = False
    command_save_config = "config save"
