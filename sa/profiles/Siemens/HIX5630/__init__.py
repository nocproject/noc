# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Siemens
## OS:     HIX5630
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH
import re

class Profile(noc.sa.profiles.Profile):
    name="Siemens.HIX5630"
    supported_schemes=[TELNET,SSH]
    pattern_more="^ --More--"
    pattern_unpriveleged_prompt=r"^\S+?>"
    pattern_syntax_error=r"% Invalid input detected at"
    command_disable_pager="terminal length 0"
    command_super="enable"
    command_enter_config="configure terminal"
    command_leave_config="exit"
    command_save_config="wr mem\n"
    pattern_prompt=r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"

    def shutdown_session(self, script):
        script.cli("terminal no length")
