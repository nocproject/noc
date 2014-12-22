# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Extreme
## OS:     XOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Extreme.XOS"
    supported_schemes = [TELNET, SSH]
    pattern_prompt = r"^(\*\s)?(Slot-\d+\s)?\S+? #"
    pattern_more = "^Press <SPACE> to continue or <Q> to quit:"
    command_more = " "
    command_disable_pager = "disable clipaging"
