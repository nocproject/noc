# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: HP
## OS:     iLO2
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="HP.iLO2"
    supported_schemes=[TELNET,SSH]
    pattern_prompt=r"hpiLO->"
    command_submit="\r"
