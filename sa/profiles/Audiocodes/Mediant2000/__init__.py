# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Audiocodes
# OS:     Mediant2000
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Profile(BaseProfile):
    name = "Audiocodes.Mediant2000"
    pattern_more = "^ -- More --"
