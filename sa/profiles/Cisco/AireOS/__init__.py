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
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.AireOS"
    pattern_username = r"^User:"
    pattern_more = r"--More-- or \(q\)uit"
    pattern_prompt = r"^\(Cisco Controller\)\s+>"
    requires_netmask_conversion = True
