# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: HP
## OS:     ProCurve
##----------------------------------------------------------------------
## Copyright (C) 2007-10 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="HP.ProCurve"
    supported_schemes=[TELNET,SSH]
    pattern_prompt=r"\S+?(\(\S+\))?# "
    pattern_unpriveleged_prompt=r"^\S+?>"
    pattern_more=[
        ("Press any key to continue","\n"),
        ("-- MORE --, next page: Space, next line: Enter, quit: Control-C"," ")
        ]
    command_disable_pager="terminal length 1000"
    command_enter_config="configure"
    command_leave_config="exit"
    command_save_config="write memory\n"
        
