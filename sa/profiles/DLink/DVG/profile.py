# ---------------------------------------------------------------------
# Vendor: DLink
# OS:     DVG
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DVG"

    submit_command = b"\r"
    username_submit = b"\n\r"
    password_submit = b"\r\n"
    pattern_username = rb"^(User: |\S+ login: )"
    pattern_more = [
        (rb"^Disconnect Now? (Y/N)", b"Y"),
        (rb"^More: <space>,  Quit: q, One line: <return>$", b" "),
    ]
    pattern_syntax_error = rb"^\s+\^\s+(\[Command Not Found\]|Option Not Found)$"
    command_enter_config = "CD /"
    command_leave_config = "SUBMIT"
    command_save_config = "SAVE"
    pattern_prompt = rb"^(>|\$) "
    command_exit = "exit"
