# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zyxel
## OS:     ZyNOSv2
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET

class Profile(noc.sa.profiles.Profile):
    name="Zyxel.ZyNOSv2"
    supported_schemes=[TELNET]
    pattern_prompt=r"^\S+?>"
    command_more=" "
