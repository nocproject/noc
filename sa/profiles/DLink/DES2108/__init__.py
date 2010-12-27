# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DES2108
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET

class Profile(noc.sa.profiles.Profile):
    name="DLink.DES2108"
    supported_schemes=[TELNET]
    pattern_prompt=r"^\S+?>"
    command_exit="logout"
    command_save_config="save"
    config_volatile=["^%.*?$"]
