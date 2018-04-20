# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Opticin
# OS:     OS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Opticin.OS"
    pattern_unprivileged_prompt = r"^(?P<hostname>[^\n]+)h>"
    pattern_syntax_error = \
        r"% Unknown command|% Invalid input detected at|" \
        r"% Incomplete command|% Ambiguous command"
=======
##----------------------------------------------------------------------
## Vendor: Opticin
## OS:     OS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET


class Profile(noc.sa.profiles.Profile):
    name = "Opticin.OS"
    supported_schemes = [TELNET]
    pattern_unpriveleged_prompt = r"^(?P<hostname>[^\n]+)h>"
    pattern_syntax_error = r"% Unknown command|% Invalid input detected at|% Incomplete command|% Ambiguous command"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>[^\n]+)\\enable>"
    pattern_more = [
        (r"----------MORE------------", " "),
        (r"--- \[Space\] Next page, \[Enter\] Next line, \[A\] All, Others to exit ---", " "),
        (r"Startup configuration file name", "\n")
    ]
    config_volatile = ["\x08+"]
    rogue_chars = ["\r"]
    command_submit = "\r"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "copy config flash"
<<<<<<< HEAD
    convert_mac = BaseProfile.convert_mac_to_dashed
=======
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_dashed
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Port15")
        'Port 15'
        """
        s = s.replace("Port1", "Port 1")
        return s.replace("Port2", "Port 2")

#    def setup_session(self, script):
#        try:
#            script.cli("terminal length 0")
#        except script.CLISyntaxError:
#            pass
