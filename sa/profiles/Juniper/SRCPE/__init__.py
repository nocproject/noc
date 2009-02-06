# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     SRC-PE
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.SRCPE"
    supported_schemes=[TELNET,SSH]
    pattern_prompt="^\S*>"
    pattern_more=r"^ -- MORE -- "
    command_more=" "
    rogue_chars=[]
