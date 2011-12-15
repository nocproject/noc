# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zyxel
## OS:     ZyNOS_EE
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
    pattern_password = "Password: "
    pattern_prompt = r"^\S+?> "
    pattern_more = r"^-- more --.*?$"
    command_more = " "
    command_exit = "exit"
    command_save_config = "config save"
    pattern_syntax_error = r"^Valid commands are:"
