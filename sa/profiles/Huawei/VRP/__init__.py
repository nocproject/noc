# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Huawei
## OS:     VRP
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile
import re


class Profile(BaseProfile):
    name = "Huawei.VRP"
    pattern_more = [
        (r"^  ---- More ----", " "),
        (r"[Cc]ontinue?\S+", "y\n\r"),
        (r"[Cc]onfirm?\S+", "y\n\r"),
        (r" [Aa]re you sure?\S+", "y\n\r"),
        (r"^Delete flash:", "y\n\r"),
        (r"^Squeeze flash:", "y\n\r")
    ]
    pattern_prompt = r"^[<#\[](?P<hostname>[a-zA-Z0-9-_\.\[\(/`\s:]+)(?:-[a-zA-Z0-9/]+)*[>#\]\)]"
    pattern_syntax_error = r"(ERROR: |% Wrong parameter found at|% Unrecognized command found at|Error:Too many parameters found|% Too many parameters found at|% Ambiguous command found at|Error: Unrecognized command found at)"

    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = "screen-length 0 temporary"
    command_enter_config = "system-view"
    command_leave_config = "return"
    command_save_config = "save"
    command_exit = "quit"
    rogue_chars = [re.compile(r"\x1b\[42D\s+\x1b\[42D"), "\r"]

    def generate_prefix_list(self, name, pl, strict=True):
        p = "ip ip-prefix %s permit %%s" % name
        if not strict:
            p += " le 32"
        return "undo ip ip-prefix %s\n" % name + "\n".join([p % x.replace("/", " ") for x in pl])

    rx_interface_name = re.compile(
        r"^(?P<type>XGE|Ten-GigabitEthernet|GE|Eth|MEth)"
        r"(?P<number>[\d/]+(\.\d+)?)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("XGE2/0/0")
        'XGigabitEthernet2/0/0'
        >>> Profile().convert_interface_name("Ten-GigabitEthernet2/0/0")
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
            "Ten-GigabitEthernet": "XGigabitEthernet",
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

    spaces_rx = re.compile("^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)

    def clean_spaces(self, config):
        config = self.spaces_rx.sub("", config)
        return config

    def fix_version(self, v):
        # CLI return S5628F-HI as platform, but SNMP return S5628F
        BAD_PLATFORMS = ["S5628F", "S5628F-HI"]
        if v["platform"] in BAD_PLATFORMS and v["version"] == "5.20":
            # Do not change these numbers. Used in get_switchport script
            v["version"] = "3.10"
        return v["version"]
