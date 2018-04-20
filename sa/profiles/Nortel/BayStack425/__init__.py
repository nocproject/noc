# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Nortel
# OS:     BayStack 425
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Nortel.BayStack425"
=======
##----------------------------------------------------------------------
## Vendor: Nortel
## OS:     BayStack 425
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Nortel.BayStack425"
    supported_schemes = [NOCProfile.TELNET]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_username = "Enter Username:"
    pattern_password = "Enter Password:"
    pattern_prompt = r"^\S+?#"
    pattern_more = [
        ("^----More", " "),
        ("ommand Line Interface...", "C"),
        ("Enter Ctrl-Y to begin", "\x19")
    ]
