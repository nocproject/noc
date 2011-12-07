# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: APC
## OS:     AOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "APC.AOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = r"^User Name\s+:"
    pattern_password = r"^Password\s+:"
    pattern_prompt = r"^>"
    pattern_more = r"^Press <ENTER> to continue...$"
    command_submit = "\r"
