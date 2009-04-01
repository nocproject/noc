# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DES-3xxx
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="DLink.DES3xxx"
    supported_schemes=[TELNET,SSH]
    pattern_username="([Uu]ser[Nn]ame|[Ll]ogin):"
    pattern_password="[Pp]ass[Ww]ord:"
    pattern_more="CTRL\+C.+?a All"
    pattern_prompt=r"^\S+?#"
    command_more="a"
    config_volatile=["^%.*?$"]
