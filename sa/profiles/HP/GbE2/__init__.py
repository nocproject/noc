# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: HP
## OS:     GbE2c
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="HP.GbE2"
    supported_schemes=[TELNET,SSH]
    pattern_more="Press q to quit, any other key to continue"
    pattern_prompt=r"^>> [^#]+# "
    command_more=" "
    command_leave_config="apply"
    command_save_config="save\ny\n"
    config_volatile=["^/\* Configuration dump taken"]
