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
    pattern_prompt = r"^(?P<hostname>\S+)#"
    pattern_syntax_error = r"% Parse error"
