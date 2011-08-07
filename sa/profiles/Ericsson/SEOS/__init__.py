# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Ericsson
## OS:     SEOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Ericsson.SEOS"
    supported_schemes = [TELNET, SSH]
    pattern_more = "^---(more)---"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    pattern_prompt = r"^\[(?P<context>\S+)\](?P<hostname>\S+)#"
