# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Allied Telesis
## OS:     AT9400
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "AlliedTelesis.AT9400"
    supported_schemes = [TELNET, SSH]
    pattern_username = "Login:"
    pattern_more = "^--More-- <Space> = next page, <CR> = one line, C = continuous, Q = quit"
    pattern_syntax_error = r"ERROR CODE = CLI_COMMAND_NOT_FOUND_OR_AMBIGUOUS"
    command_more = "c"
    command_submit = "\r"
    command_save_config = "save configuration"
    pattern_prompt = r"^\S*[\$#] "
    command_exit = "quit"
