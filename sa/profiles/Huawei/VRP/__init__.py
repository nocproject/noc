# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Huawei
## OS:     VRP
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.profiles import Profile as NOCProfile
import re


class Profile(noc.sa.profiles.Profile):
    name = "Huawei.VRP"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = [
        (r"^  ---- More ----", " "),
        (r"[Cc]ontinue?\S+", "y\n\r")
    ]
    pattern_prompt = r"^[<#\[](?P<hostname>[a-zA-Z0-9-_\.]+)(?:-[a-zA-Z0-9/]+)*[>#\]]"
    pattern_syntax_error = r"^Error: "
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = "screen-length 0 temporary"
    command_enter_config = "system-view"
    command_leave_config = "return"
    command_save_config = "save"
    command_exit = "quit"

    def generate_prefix_list(self, name, pl, strict=True):
        p = "ip ip-prefix %s permit %%s" % name
        if not strict:
            p += " le 32"
        return "undo ip ip-prefix %s\n" % name + "\n".join([p % x.replace("/", " ") for x in pl])

    rx_interface_name = re.compile(
        r"^(?P<type>XGE|GE|Eth|MEth)(?P<number>[\d/]+(\.\d+)?)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("XGE2/0/0")
        'XGigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("GE2/0/0")
        'GigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("Eth2/0/0")
        'Ethernet2/0/0'
        >>> Profile().convert_interface_name("MEth2/0/0")
        'M-Ethernet2/0/0'
        """
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        return "%s%s" % ({
            "XGE": "XGigabitEthernet",
            "GE": "GigabitEthernet",
            "Eth": "Ethernet",
            "MEth": "M-Ethernet",
            # "Vlanif": "Vlan-interface" - need testing
        }[match.group("type")], match.group("number"))

    def convert_mac(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 0011-2233-4455
        """
        v = mac.replace(":", "").lower()
        return "%s-%s-%s" % (v[:4], v[4:8], v[8:])
