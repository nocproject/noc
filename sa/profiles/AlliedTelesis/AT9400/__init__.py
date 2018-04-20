# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT9400
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT9400"
    pattern_more = \
        "^--More-- <Space> = next page, <CR> = one line, C = continuous, " \
        "Q = quit"
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"ERROR CODE = CLI_COMMAND_NOT_FOUND_OR_AMBIGUOUS"
    command_more = "c"
    command_submit = "\r"
    command_save_config = "save configuration"
<<<<<<< HEAD
    pattern_prompt = r"^\S*[\$#] $"
=======
    pattern_prompt = r"^\S*[\$#] "
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_exit = "quit"
