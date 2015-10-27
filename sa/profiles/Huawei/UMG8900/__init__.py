# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Huawei
## OS:     UMG8900 media gateway
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.UMG8900"
    pattern_username = "Login :"
    pattern_password = "Password :"
    pattern_more = r"^Press CTRL\+C to break, other key to continue\.\.\."
    pattern_prompt = r"mml>"
    command_more = " "
    rogue_chars = ["\r"]
    config_volatile = [r"^\+\+\+.*?$"]
