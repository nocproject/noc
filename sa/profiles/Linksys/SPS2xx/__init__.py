# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Linksys
## OS:     SPS2xx
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
    name="Linksys.SPS2xx"
    supported_schemes=[TELNET,SSH]
    pattern_username="User Name:"
    pattern_password="Password:"
    pattern_more="More: <space>.+?<return>"
    pattern_prompt=r"^\S+?#"
    command_more=" "
