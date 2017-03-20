# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Willis
## OS:     FWBD
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
'''
'''

from noc.core.profile.base import BaseProfile
import re

class Profile(BaseProfile):
    name = "Wilis.FWBD"
    pattern_prompt = r"^(?P<hostname>\S+)\s*>?"
    pattern_username = "[Ll]ogin: "
    pattern_password = "[Pp]assword: "
    command_submit = "\r"
    command_exit = "logout"

