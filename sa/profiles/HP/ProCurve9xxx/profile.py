# ---------------------------------------------------------------------
# Vendor: HP
# OS:     ProCurve9xxx
# ---------------------------------------------------------------------
# Copyright (C) 2007-10 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.ProCurve9xxx"

    pattern_prompt = rb"\S+?(\(\S+\))?#"
    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_username = rb"User"
    command_disable_pager = "terminal length 1000"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write memory\n"
    command_super = "enable"
    command_exit = "exit"
