# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## HW:     7324 RU
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, HTTP


class Profile(noc.sa.profiles.Profile):
    name = "Alcatel.7324RU"
    supported_schemes = [TELNET, HTTP]
    pattern_username = "User name:"
    pattern_password = "Password:"
    pattern_prompt = "^\S+>"
    command_save_config = "config save"
    command_exit = "exit"
