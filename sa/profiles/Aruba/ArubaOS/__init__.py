# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Aruba
## OS:     ArubaOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Aruba.ArubaOS"
    supported_schemes = [NOCProfile.SSH]
    pattern_username = "Username"
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"% Parse error"
    command_super = "enable"
    pattern_more = [
        (r"--More-- \(q\) quit \(u\) pageup \(/\) search \(n\) repeat", " ")
    ]