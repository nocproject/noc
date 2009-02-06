# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: MikroTik
## OS:     RouterOS
## Compatible: 2.8, 2.9
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="MikroTik.RouterOS"
    supported_schemes=[TELNET,SSH]
    command_submit="\r"
    pattern_prompt=r"^\[.+?@.+?\] >"
    config_volatile=["^#.*?$"]
