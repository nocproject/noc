# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: HP
## OS:     ProCurve9xxx
##----------------------------------------------------------------------
## Copyright (C) 2007-10 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.ProCurve9xxx"
    pattern_prompt = r"\S+?(\(\S+\))?#"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_username = r"User"
    command_disable_pager = "terminal length 1000"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write memory\n"
    command_super = "enable"
    command_exit = "exit"
