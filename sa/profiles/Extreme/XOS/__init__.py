# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Extreme
## OS:     XOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Extreme.XOS"
    pattern_prompt = r"^(\*\s)?\S+? #"
    pattern_more = "^Press <SPACE> to continue or <Q> to quit:"
    command_more = " "
    command_disable_pager = "disable clipaging"
