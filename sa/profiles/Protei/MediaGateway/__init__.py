# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Protei
## OS:     MAK, MTU, ITG
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Protei.MediaGateway"
    supported_schemes=[TELNET,SSH]
    command_submit="\r"
    pattern_prompt="(^\S+\$|MAK>|MTU>|ITG>)"
