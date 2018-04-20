# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: NAG
# OS:     SNR
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NAG.SNR"
    pattern_more = [
        (r"^ --More-- ", "\n")
    ]
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    command_disable_pager = "terminal length 0"
    command_exit = "exit"
=======
##----------------------------------------------------------------------
## Vendor: NAG
## OS:     SNR
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "NAG.SNR"
    supported_schemes = [NOCProfile.HTTP, NOCProfile.SSH, NOCProfile.TELNET]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
