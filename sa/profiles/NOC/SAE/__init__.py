# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: NOC
## OS:     SAE
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles


class Profile(noc.sa.profiles.Profile):
    name="NOC.SAE"
    supported_schemes = [0]  # Fake telnet

