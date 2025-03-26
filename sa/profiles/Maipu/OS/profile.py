# ---------------------------------------------------------------------
# Vendor: Maipu
# OS:     OS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Maipu.OS"

    pattern_more = [
        (rb"^---MORE---", b" "),
        (rb"^....press ENTER to next line, Q to quit, other key to next page....", b"\n"),
        (rb"Startup config in flash will be updated, are you sure", b"y"),
    ]

    command_exit = "quit"
    command_super = b"enable"
    command_enter_config = "configure t"
    command_leave_config = "end"
    command_save_config = "save"

    pattern_syntax_error = rb"% Unrecognized command, and error detected at \'^\' marker."
    pattern_unprivileged_prompt = rb"^(?P<hostname>[a-zA-Z0-9-_\.]+)(?:-[a-zA-Z0-9/]+)*>$"
    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9-_\.]+)(?:-[a-zA-Z0-9/]+)(\(config\))*[*\)>#]$"
