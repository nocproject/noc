# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Vyatta
## OS:     Vyatta
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Vyatta.Vyatta"
    supported_schemes=[TELNET,SSH]
    pattern_username=r"[Ll]ogin: (?!\S+)"
    pattern_prompt=r"^(?P<username>\S+)@(?P<hostname>\S+):[^$]+\$ "
    pattern_more=r"^:"
    command_more=" "
    command_disable_pager="terminal length 0"
    command_enter_config="configure"
    command_leave_config="commit\nexit"
