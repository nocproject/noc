# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Linksys
# OS:     SPS2xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Linksys.SPS2xx"
    pattern_more = r"^More: <space>,  Quit: q, One line: <return>$"
    pattern_unprivileged_prompt = r"^\S+> "
=======
##----------------------------------------------------------------------
## Vendor: Linksys
## OS:     SPS2xx
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Linksys.SPS2xx"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = r"^User Name:"
    pattern_password = r"^Password:"
    pattern_more = r"^More: <space>,  Quit: q, One line: <return>$"
    pattern_unpriveleged_prompt = r"^\S+> "
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"^% (Unrecognized command|Incomplete command|Wrong number of parameters or invalid range, size or characters entered)$"
    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = r"^\S+# "
