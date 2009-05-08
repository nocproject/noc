# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: InfiNet
## OS:     WANFlexX
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET

class Profile(noc.sa.profiles.Profile):
    name="InfiNet.WANFlexX"
    supported_schemes=[TELNET]
    pattern_more="^-- more --"
    pattern_prompt=r"\S+?#\d+>"
    command_submit="\r"
    command_more=" "
