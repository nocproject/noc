# -*- coding: utf-8 -*-
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
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Opticin.OS"
    pattern_unpriveleged_prompt = r"^(?P<hostname>[^\n]+)h>"
    pattern_syntax_error = r"% Unknown command|% Invalid input detected at|% Incomplete command|% Ambiguous command"
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
    convert_mac = BaseProfile.convert_mac_to_dashed

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
