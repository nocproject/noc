# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Allied Telesis
## OS:     AT9900
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "AlliedTelesis.AT9900"
    supported_schemes = [TELNET, SSH]
    pattern_username = r"^.*\slogin: "
    pattern_more = r"^--More--.*"
    command_more = "c"
    command_submit = "\r"
    command_save_config = "create config=boot1.cfg"
    pattern_prompt = r"^Manager.*>"
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_cisco
