# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zyxel
## OS:     ZyNOS_EE
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.ZyNOS_EE"
    pattern_password = "Password: "
    pattern_prompt = r"^\S+?> "
    pattern_more = r"^-- more --.*?$"
    command_more = " "
    command_exit = "exit"
    command_save_config = "config save"
    pattern_syntax_error = r"^Valid commands are:"
