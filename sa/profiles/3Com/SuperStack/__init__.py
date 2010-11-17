# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: 3Com
## OS:     SuperStack
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="3Com.SuperStack"
    supported_schemes=[TELNET]
    pattern_username="Login:"
    pattern_password="Password:"
    pattern_prompt=r"^Select menu option.*:"
    pattern_more=[(r"Escape character is '\^\]'\.", "\n")]
    command_submit="\r"
