# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## OS:     TIMOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Alcatel.TIMOS"
    supported_schemes = [TELNET, SSH]
    pattern_username = "[Ll]ogin: "
    pattern_password = "[Pp]assword: "
    command_disable_pager = "environment no more"
    command_exit="logout"
    pattern_prompt = r"^\S+?#"
    config_volatile = [r"^# Finished.*$", r"^# Generated.*$"]
    pattern_more = r"^Press any key to continue.*$"
    command_more = " "
