# ---------------------------------------------------------------------
# Vendor: Nateks
# OS:     FlexFain ACE 8/16
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Nateks.FlexGainACE16"

    pattern_more = [
        (rb"^logged on; type `exit' to close connection.", b"\n"),
        (rb"^Press 'y' to continue, 'n' to break and press Enter", b"\n"),
        (rb"^Yes or No <y/n>", b"y\n"),
    ]
    pattern_syntax_error = rb"% Unknown action |% Ambiguous command:"
    pattern_username = rb"user:"
    pattern_password = rb"[Pp]assword:"
    command_submit = b"\n"

    pattern_prompt = rb"^IPDSLAM#"
    command_exit = "exit"
    command_save_config = "commit\n"
