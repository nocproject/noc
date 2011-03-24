# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zyxel
## OS:     ZyNOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Zyxel.ZyNOS"
    supported_schemes=[TELNET,SSH]
    pattern_username="User name:"
    pattern_unpriveleged_prompt=r"^\S+?>"
    pattern_prompt=r"^\S+?#"
    pattern_more=r"^-- more --.*?$" 
    command_super="enable"
    command_more=" "
    command_enter_config="configure" 
    command_leave_config="exit" 
    command_exit="exit" 
    command_save_config="write memory" 
    pattern_syntax_error="Invalid command"
