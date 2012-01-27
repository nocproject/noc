# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Allied Telesis
## OS:     AT8500
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "AlliedTelesis.AT8500"
    supported_schemes = [TELNET, SSH]
    pattern_username = "Login:"
    pattern_more = "^--More-- <Space> = next page, <CR> = one line, C = continuous, Q = quit"
    command_more = "c"
    command_submit = "\r"
    command_save_config = "save configuration"
    pattern_prompt = r"^\S+?#"
