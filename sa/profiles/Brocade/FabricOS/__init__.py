# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Brocade
## OS:     FabricOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Brocade.FabricOS"
    supported_schemes = [TELNET, SSH]
    pattern_prompt = r"\S+:\S+>"
