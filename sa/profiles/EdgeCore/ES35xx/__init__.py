# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: EdgeCore
## OS:     ES35xx
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH
import re

class Profile(noc.sa.profiles.Profile):
    name="EdgeCore.ES35xx"
    supported_schemes=[TELNET,SSH]
    pattern_unpriveleged_prompt=r"^\S+?>"
    pattern_prompt=r"^\S+?#"
    pattern_more="^---More---.*?$"
    command_more=" "
    rogue_chars=["\r",re.compile(r" *\x08+")]

