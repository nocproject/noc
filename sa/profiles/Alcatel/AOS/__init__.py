# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## OS:     AOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Alcatel.AOS"
    supported_schemes=[TELNET,SSH]
    pattern_username="[Ll]ogin :"
    pattern_password="[Pp]assword :"
    pattern_prompt=r"^\S*->"
