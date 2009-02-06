# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DES-35xx
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="DLink.DES35xx"
    supported_schemes=[TELNET,SSH]
    pattern_more="^CTRL\+C.+?a All"
    pattern_prompt=r"^\S+?#"
    command_more="a"
    config_volatile=["^%.*?$"]
