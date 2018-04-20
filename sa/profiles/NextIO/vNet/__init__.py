# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: NextIO
# OS:     vNet
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NextIO.vNet"
=======
##----------------------------------------------------------------------
## Vendor: NextIO
## OS:     vNet
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "NextIO.vNet"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"^ERROR: Invalid command -"
    pattern_operation_error = r"^ERROR: "
    pattern_prompt = r"^(?P<hostname>\S+)> "
