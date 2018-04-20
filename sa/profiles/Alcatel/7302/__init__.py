# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Vendor: Alcatel
# HW:     7302/7330
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.7302"
    pattern_prompt = r"^(?:typ:|leg:|)\S+(?:>|#)"
    pattern_syntax_error = r"invalid token"
    pattern_more = r"Press <space>\(page\)/<enter>\(line\)/q\(quit\) to continue..."
    command_save_config = "admin software-mngt shub database save"
    command_exit = "logout"
    command_more = " "
=======
##----------------------------------------------------------------------
## Vendor: Alcatel
## HW:     7302/7330
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET


class Profile(noc.sa.profiles.Profile):
    name = "Alcatel.7302"
    supported_schemes = [TELNET]
    pattern_username = "[Ll]ogin:"
    pattern_password = "[Pp]assword:"
    pattern_prompt = r"^leg:.+#"
    command_save_config = "admin software-mngt shub database save"
    command_exit = "logout"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
