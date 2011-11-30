# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: 3Com
## OS:     SuperStack
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET


class Profile(noc.sa.profiles.Profile):
    name = "3Com.SuperStack"
    supported_schemes = [TELNET]
    pattern_username = "Login:"
    pattern_password = "Password:"
    pattern_prompt = r"^Select menu option.*:"
    pattern_more = [
        (r"Enter <CR> for more or 'q' to quit--:", "\r"),
    ]
    command_submit = "\r"
    telnet_send_on_connect = "\r"
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_dashed
