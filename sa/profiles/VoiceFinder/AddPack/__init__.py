# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: VoiceFinder
## OS:     AddPack
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="VoiceFinder.AddPack"
    supported_schemes=[TELNET,SSH]
    pattern_more="^-- more --"
    pattern_prompt=r"^\S+?#"
    command_more=" \n"
    command_submit="\r"

