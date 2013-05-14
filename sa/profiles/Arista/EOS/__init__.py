# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Arista
## OS:     EOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Arista.EOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)>"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    pattern_syntax_error = r"% Invalid input"
    pattern_username = "Login:"
    pattern_more = [
        (r"^ --More--", "\n"),
        (r"\?\s*\[confirm\]", "\n")
    ]
    command_submit = "\r"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    convert_mac = NOCProfile.convert_mac_to_cisco
