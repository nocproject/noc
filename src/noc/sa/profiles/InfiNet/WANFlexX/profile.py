# ---------------------------------------------------------------------
# Vendor: InfiNet
# OS:     WANFlexX
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "InfiNet.WANFlexX"

    pattern_more = [(rb"^-- more --$", b" ")]
    pattern_prompt = rb"(?P<hostname>\S+?)[#|\$]\d+>"
    command_submit = b"\r"
    username_submit = b"\r"
    password_submit = b"\r"
    command_exit = "exit"
    pattern_syntax_error = rb"Unknown command\. Use \? for help"
