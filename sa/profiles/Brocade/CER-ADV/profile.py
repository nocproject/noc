# ---------------------------------------------------------------------
# Vendor: Brocade
# OS:     CER-ADV
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Brocade.CER-ADV"

    pattern_more = [(rb"--More--", b" ")]
    # pattern_prompt = "\\S+?(\\(\\S+\\))?#"
    pattern_prompt = rb"^\\S*@(?P<hostname>[a-zA-Z0-9]\\S*?)(?:-\\d+)?(?:\\(config[^\\)]*\\))?#"
    pattern_unprivileged_prompt = rb"^\\S+?>"
    pattern_syntax_error = rb"Invalid input ->|Ambiguous input ->|Incomplete command."
    pattern_username = "Login"
    username_submit = b"\r"
    password_submit = b"\r"
    command_disable_pager = "skip-page-display"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_save_config = "write memory"
    command_super = b"enable"
    command_exit = "exit/rexit"
    command_submit = b"\r"
