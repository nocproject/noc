# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: AddPac
## OS:     APOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="AddPac.APOS"
    supported_schemes=[TELNET,SSH]
    pattern_more="^-- more --"
    pattern_prompt=r"^\S+?#"
    command_more=" \n"
    command_submit="\r"
    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"

