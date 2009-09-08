# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     AireOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Cisco.AireOS"
    supported_schemes=[TELNET,SSH]
    pattern_username=r"^User:"
    pattern_more=r"--More-- or \(q\)uit"
    pattern_prompt=r"^\(Cisco Controller\)\s+>"
    requires_netmask_conversion=True
