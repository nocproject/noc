# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: ZTE
# OS:     ZXA10
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXA10"
    pattern_more = r"^ --More--"
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = r"%Error \d+: (Incomplete command|Invalid input)"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write\n"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco
    config_volatile = [r"^ntp clock-period .*?^"]
    telnet_naws = b"\x7f\x7f\x7f\x7f"

    rx_card = re.compile(
        r"1\s+(?P<shelf>\d+)\s+(?P<slot>\d+)\s+"
        r"(?P<cfgtype>\S+)\s+(?P<realtype>\S+|)\s+(?P<port>\d+)\s+"
        r"(?P<hardver>\d+|)\s+(?P<softver>V\S+|)\s+(?P<status>INSERVICE|OFFLINE|STANDBY)"
    )

    def fill_ports(self, script):
        r = []
        v = script.cli("show card")
        for line in v.splitlines():
            match = self.rx_card.search(line)
            if match:
                r += [match.groupdict()]
        return r
