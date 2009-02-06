# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: ZTE
## OS:     ZXDSL531
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,HTTP

class Profile(noc.sa.profiles.Profile):
    name="ZTE.ZXDSL531"
    supported_schemes=[TELNET,HTTP]
    pattern_username="Login name:"
    pattern_password="Password:"
    pattern_prompt="^>"
    config_volatile=["<entry1 sessionID=.+?/>"]
    
