# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: ZTE
## OS:     ZXDSL531
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXDSL531"
    pattern_username = "Login name:"
    pattern_password = "Password:"
    pattern_prompt = "^>"
    config_volatile = ["<entry1 sessionID=.+?/>"]
