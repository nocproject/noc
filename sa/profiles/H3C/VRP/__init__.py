# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: H3C
## OS:     VRP
## Compatible: 3.1
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH
import re


class Profile(noc.sa.profiles.Profile):
    name = "H3C.VRP"
    supported_schemes = [TELNET, SSH]
    pattern_more = "^  ---- More ----"
    pattern_prompt = r"^[<#]\S+?[>#]"
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = ""

    def generate_prefix_list(self, name, pl, strict=True):
        p = "ip ip-prefix %s permit %%s" % name
        if not strict:
            p += " le 32"
        return "undo ip ip-prefix %s\n" % name + "\n".join([p % x.replace("/", " ") for x in pl])

    rx_interface_name = re.compile(r"^(?P<type>[A-Z]+E)(?P<number>[\d/]+)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("GE2/0/0")
        'GigabitEthernet2/0/0'
        """
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        return "%s%s" % ({"GE": "GigabitEthernet"}[match.group("type")], match.group("number"))

    def clean_spaces(self, config):
        rx = re.compile("^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)
        config = rx.sub("", config)
        return config
