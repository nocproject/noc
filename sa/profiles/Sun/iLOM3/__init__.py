# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Sun
## OS:     iLOM3
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Sun.iLOM3"
    pattern_prompt = r"^(?:\S* )?->"
