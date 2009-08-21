# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     NX-OS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Cisco.NXOS"
    supported_schemes=[TELNET,SSH]
    pattern_more="^--More--"
    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"
    pattern_prompt=r"^\S+?#"
    requires_netmask_conversion=True
    convert_mac=noc.sa.profiles.Profile.convert_mac_to_cisco
