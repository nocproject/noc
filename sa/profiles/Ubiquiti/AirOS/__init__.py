# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Ubiquiti
## OS:     AirOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ubiquiti.AirOS"
    pattern_username = "([Uu][Bb][Nn][Tt] login|[Ll]ogin):"
    pattern_password = "[Pp]assword:"
    pattern_more = "CTRL\+C.+?a All"
    pattern_prompt = r"^\S+?\.v(?P<version>\S+)#"
    command_more = "a"
    config_volatile = ["^%.*?$"]
