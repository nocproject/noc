# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     JUNOSe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.JUNOSe"
    supported_schemes=[TELNET,SSH]
    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"
    pattern_prompt=r"^\S+?#"
    pattern_more=r"^ --More-- "
    command_more=" "
    config_volatile=["^! Configuration script being generated on.*?^",r"^Please wait\.\.\."]
    rogue_chars=["\r","\x00","\x0d"]
