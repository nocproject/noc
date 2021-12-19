# ---------------------------------------------------------------------
# Vendor: Nateks
# OS:     FlexFain
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
Test in FlexGain ACE24 DSLAM
"""

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Nateks.FlexGainACE24"
    pattern_more = [(rb"^Login Successful------", b"\n\r")]
    pattern_syntax_error = (
        rb"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    )
    pattern_username = br"[Ll]ogin:"
    pattern_password = rb"[Pp]assword:"

    pattern_prompt = rb"(^\$\s+|^>\s)"
    # pattern_unprivileged_prompt = r"$\s"
    command_exit = "exit"
    command_save_config = "commit\n"
