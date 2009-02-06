# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Huawei
## OS:     UMG8900 media gateway
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET

class Profile(noc.sa.profiles.Profile):
    name="Huawei.UMG8900"
    supported_schemes=[TELNET]
    pattern_username="Login :"
    pattern_password="Password :"
    pattern_more=r"^Press CTRL\+C to break, other key to continue\.\.\."
    pattern_prompt=r"mml>"
    command_more=" "
    rogue_chars=["\r"]
    config_volatile=[r"^\+\+\+.*?$"]
