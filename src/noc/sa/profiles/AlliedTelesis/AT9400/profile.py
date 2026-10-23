# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT9400
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT9400"

    pattern_more = [
        (rb"^--More-- <Space> = next page, <CR> = one line, C = continuous, Q = quit", b"c")
    ]
    pattern_syntax_error = rb"ERROR CODE = CLI_COMMAND_NOT_FOUND_OR_AMBIGUOUS"
    command_submit = b"\r\n"
    username_submit = b"\r\n"
    password_submit = b"\r\n"
    command_save_config = "save configuration"
    pattern_prompt = rb"^\S*[\$#] $"
    command_exit = "quit"
