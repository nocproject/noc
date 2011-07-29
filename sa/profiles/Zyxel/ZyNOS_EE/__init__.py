# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zyxel
## HW:     EE
## OS:     ZyNOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Zyxel.ZyNOS_EE"
    supported_schemes = [TELNET, SSH]
#    pattern_username="User name:"
    pattern_password = "Password:"
#    pattern_unpriveleged_prompt=r"^\S+?>"
    pattern_prompt = r"^\S+?>"
    pattern_more = r"^-- more --.*?$"
    command_super = "enable"
    command_more = " "
    command_enter_config = "config"
    command_leave_config = "exit"
    command_exit = "exit"
    command_save_config = "config save"
    pattern_syntax_error = "Invalid command"
