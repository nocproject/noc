# -*- coding: utf-8 -*-
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
