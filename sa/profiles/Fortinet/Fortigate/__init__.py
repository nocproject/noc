# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Fortinet
## OS:     FortiOS v4.X
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Fortinet.Fortigate"
    supported_schemes = [TELNET, SSH]
    pattern_more = "^--More--"
    pattern_prompt = r"^\S+\ #"
    command_more = " "
