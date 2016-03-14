# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Raisecom
## OS:     ROS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Raisecom.ROS"
    pattern_more = "^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^\S+?#"
    command_more = " "
