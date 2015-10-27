# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     ScreenOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile

class Profile(BaseProfile):
    name="Juniper.ScreenOS"
    pattern_prompt=r"^\s*\S*-> "
    pattern_more=r"^--- more ---"
    command_more=" "
    #command_disable_pager="set console page 0"
