# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## OS:     AOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.AOS"
    pattern_username = "[Ll]ogin :"
    pattern_password = "[Pp]assword :"
    pattern_prompt = r"^(\S*->|(?P<hostname>\S+)# )"
    command_save_config = "write memory\r\ncopy working certified"
