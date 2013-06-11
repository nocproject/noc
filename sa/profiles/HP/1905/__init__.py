# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: HP
## OS:     1905
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "HP.1905"
    supported_schemes = [NOCProfile.HTTP, NOCProfile.TELNET]
