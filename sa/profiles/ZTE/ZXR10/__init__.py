# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: ZTE
## OS:     ZXR10
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "ZTE.ZXR10"
    supported_schemes = [TELNET, SSH]
    pattern_more = r"^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write\n"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_cisco
    config_volatile = [r"^ntp clock-period .*?^"]
    telnet_naws = "\x7f\x7f\x7f\x7f"
