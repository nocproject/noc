# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     RG
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.RG"

    pattern_username = rb"^\S+ [Ll]ogin:"
    pattern_password = rb"^[Pp]assword:"
    pattern_syntax_error = rb"Permission denied"
    pattern_unprivileged_prompt = rb"^\S+@(?P<hostname>\S+):~\$"
    pattern_prompt = rb"^\S+@(?P<hostname>\S+):~#"
    command_exit = "exit"
    command_more = "\n"

    PLATFORMS = {"46": "RG-1404GF-W"}

    @classmethod
    def get_platforms(cls, name):
        return cls.PLATFORMS.get(name)
