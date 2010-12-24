# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: EdgeCore
## OS:     ES
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH
import re

class Profile(noc.sa.profiles.Profile):
    name="EdgeCore.ES"
    supported_schemes=[TELNET,SSH]
    pattern_unpriveleged_prompt=r"^(?P<hostname>[^\n]+)>"
    pattern_syntax_error=r"% Invalid input detected at"
    command_super="enable"
    pattern_prompt=r"^(?P<hostname>[^\n]+)#"
    pattern_more=r"---?More---?"
    command_more=" "
    config_volatile=["\x08+"]
    rogue_chars=["\r"]
    command_submit="\r"
    convert_mac=noc.sa.profiles.Profile.convert_mac_to_dashed
    
    def convert_interface_name(self, s):
	return s.replace("/ ","/")
