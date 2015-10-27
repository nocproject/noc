# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Brocade
## OS:     FabricOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Brocade.FabricOS"
    pattern_prompt = r"\S+:\S+>"
