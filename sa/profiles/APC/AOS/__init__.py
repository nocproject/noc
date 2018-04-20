# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Vendor: APC
# OS:     AOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "APC.AOS"
    pattern_username = r"^User Name\s+:"
    username_submit = "\r"
    pattern_password = r"^Password\s+:"
    password_submit = "\r"
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_prompt = r"^(\S+)?>"
    pattern_more = r"^Press <ENTER> to continue...$"
    command_submit = "\r"
