# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: AddPac
## OS:     APOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AddPac.APOS"
    pattern_more = "^-- more --"
    pattern_prompt = r"^\S+?#"
    command_more = " \n"
    command_submit = "\r"
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
