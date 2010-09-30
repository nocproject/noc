# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     ScreenOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.ScreenOS"
    supported_schemes=[TELNET,SSH]
    pattern_prompt=r"^\s*\S*-> "
    pattern_more=r"^--- more ---"
    command_more=" "
    #command_disable_pager="set console page 0"
