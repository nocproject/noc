# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Foundry
## OS:     IronWare
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Brocade.IronWare"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_prompt = r"\S+?(\(\S+\))?#"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_username = r"User"
    command_disable_pager = "terminal length 1000"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write memory\n"
    command_super = "enable"
