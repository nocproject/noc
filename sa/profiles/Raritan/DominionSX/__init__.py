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
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Raritan.DominionSX"
    pattern_prompt = r"^(\S+ > )+"
    pattern_more = "--More-- Press <ENTER> to continue."
