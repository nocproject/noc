# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: HP
## OS:     Comware
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "HP.Comware"
    supported_schemes = [TELNET]
    pattern_more = [(r"^.+---- More ----$", " ")]
    command_more = " "
    pattern_prompt = r"^[<\[]\S+[>\]]"
    command_exit = "quit"
    rogue_chars = [
        re.compile(r"                "),
        "\r"
    ]

