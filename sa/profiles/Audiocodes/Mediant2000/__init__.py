# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Audiocodes
## OS:     Mediant2000
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Audiocodes.Mediant2000"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH, NOCProfile.HTTP]
    pattern_more = "^ -- More --"

