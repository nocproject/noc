# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: EdgeCore
## OS:     ES
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "EdgeCore.ES"
    supported_schemes = [TELNET, SSH]
    pattern_unpriveleged_prompt = r"^(?P<hostname>[^\n]+)>"
    pattern_syntax_error = r"% Invalid input detected at|% Incomplete command"
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>[^\n]+)(?:\(config[^)]*\))?#"
    pattern_more = [
        (r"---?More---?", " "),
        (r"--- \[Space\] Next page, \[Enter\] Next line, \[A\] All, Others to exit ---", " "),
        (r"Startup configuration file name", "\n")
    ]
    config_volatile = ["\x08+"]
    rogue_chars = ["\r"]
    command_submit = "\r"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config"
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_dashed

    def convert_interface_name(self, s):
        s = s.replace("  ", " ")
        return s.replace("/ ", "/")

    def setup_session(self, script):
        try:
            script.cli("terminal length 0")
        except script.CLISyntaxError:
            pass
