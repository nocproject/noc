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
from noc.core.profile.base import BaseProfile

class Profile(BaseProfile):
    name="Cisco.1900"

    pattern_more=[  ("\[K\] Command Line", "K"),
                    ("--More--$", " ")
                    ]

    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"
    convert_mac = BaseProfile.convert_mac_to_cisco
