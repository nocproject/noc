# ---------------------------------------------------------------------
# Vendor: Foundry
# OS:     IronWare
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Brocade.IronWare"

    pattern_prompt = rb"\S+?(\(\S+\))?#"
    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_username = rb"User"
    command_disable_pager = "terminal length 1000"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write memory\n"
    command_super = b"enable"
    pattern_more = [
        (rb"^--More--, next page: Space, next line: Return key, quit: Control-c", b" "),
    ]
