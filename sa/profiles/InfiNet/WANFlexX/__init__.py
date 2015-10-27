# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: InfiNet
## OS:     WANFlexX
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "InfiNet.WANFlexX"
    pattern_more = "^-- more --"
    pattern_prompt = r"\S+?#\d+>"
    command_submit = "\r"
    command_more = " "
    command_exit = "exit"
