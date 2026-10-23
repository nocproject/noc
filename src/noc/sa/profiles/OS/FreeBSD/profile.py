# ---------------------------------------------------------------------
# Vendor: FreeBSD
# OS:     FreeBSD
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "OS.FreeBSD"

    command_super = b"su"
    command_exit = "exit"
    pattern_username = rb"^[Ll]ogin:"
    pattern_unprivileged_prompt = rb"^\S*?\s*(%|\$)\s*$"
    pattern_prompt = rb"^(?P<hostname>\S*)\s*#\s*$"
    pattern_syntax_error = rb": Command not found\."
