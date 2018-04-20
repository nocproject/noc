# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Aruba
# OS:     ArubaOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Aruba.ArubaOS"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
=======
##----------------------------------------------------------------------
## Vendor: Aruba
## OS:     ArubaOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Aruba.ArubaOS"
    supported_schemes = [NOCProfile.SSH]
    pattern_username = "Username"
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)\s*>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"% Parse error"
    command_super = "enable"
    pattern_more = [
        (r"--More-- \(q\) quit \(u\) pageup \(/\) search \(n\) repeat", " ")
    ]
    rogue_chars = [
        re.compile(r"\r\s+\r"),
        "\r"
<<<<<<< HEAD
    ]
=======
    ]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
