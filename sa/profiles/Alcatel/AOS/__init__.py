# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## OS:     AOS
## Compatible: OS LS6224
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Alcatel.AOS"
    supported_schemes=[TELNET,SSH]
    pattern_username="User Name:"
    pattern_more="^More: .*?$"
    command_more=" "
