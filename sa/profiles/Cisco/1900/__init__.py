# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     1900
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET

class Profile(noc.sa.profiles.Profile):
    name="Cisco.1900"
    supported_schemes=[TELNET]

    pattern_more=[  ("\[K\] Command Line", "K"),
                    ("--More--$", " ")
                    ]

    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_cisco
