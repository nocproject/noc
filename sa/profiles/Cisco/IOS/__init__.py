# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     IOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Cisco.IOS"
    supported_schemes=[TELNET,SSH]
    pattern_more="^ --More--"
    pattern_unpriveleged_prompt=r"^\S+?>"
    pattern_syntax_error=r"% Invalid input detected at"
    command_disable_pager="terminal length 0"
    command_super="enable"
    command_enter_config="configure terminal"
    command_leave_config="exit"
    command_save_config="copy running-config startup-config\n"
    pattern_prompt=r"^(?P<hostname>\S+?)(?:\(config[^\)]*\))?#"
    requires_netmask_conversion=True
    convert_mac=noc.sa.profiles.Profile.convert_mac_to_cisco
    convert_interface_name=noc.sa.profiles.Profile.convert_interface_name_cisco
    config_volatile=["^ntp clock-period .*?^"]
    
    def generate_prefix_list(self,name,pl,strict=True):
        p="ip prefix-list %s permit %%s"%name
        if not strict:
            p+=" le 32"
        return "no ip prefix-list %s\n"%name+"\n".join([p%x for x in pl])
    
##
## uBR series selector
##
def uBR(v):
    return "BC" in v["version"]
