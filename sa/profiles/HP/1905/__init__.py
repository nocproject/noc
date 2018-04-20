# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: HP
# OS:     1905
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.1905"
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
