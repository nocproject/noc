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
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXR10"
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
    convert_mac = BaseProfile.convert_mac_to_cisco
    config_volatile = [r"^ntp clock-period .*?^"]
    telnet_naws = "\x7f\x7f\x7f\x7f"
