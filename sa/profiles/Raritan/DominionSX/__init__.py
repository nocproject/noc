# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Raritan
## OS:     DominionSX
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import SSH

class Profile(noc.sa.profiles.Profile):
    name="Raritan.DominionSX"
    supported_schemes=[SSH]
    pattern_prompt=r"^(\S+ > )+"
    pattern_more="--More-- Press <ENTER> to continue."
