# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Force10
## OS:     FTOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Force10.FTOS"
    supported_schemes=[TELNET,SSH]
    pattern_more="^ --More--"
    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"
    command_enter_config="configure terminal"
    command_leave_config="exit"
    command_save_config="write memory"
    pattern_prompt=r"^\S+?#"
    command_submit="\r"
    
    def generate_prefix_list(self,name,pl,strict=True):
        suffix=""
        if not strict:
            suffix+=" le 32"
        p="no ip prefix-list %s\n"%name
        p+="ip prefix-list %s\n"%name
        p+="\n".join(["    permit %s%s"%(x,suffix) for x in pl])
        p+="\nexit\n"
        return p
