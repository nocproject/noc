# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: H3C
# OS:     VRP
# Compatible: 3.1
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "H3C.VRP"
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_more = "^  ---- More ----"
    pattern_prompt = r"^[<#]\S+?[>#]"
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = ""
<<<<<<< HEAD
    pattern_syntax_error = r"% Wrong parameter|% Unrecognized command found at"
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def generate_prefix_list(self, name, pl, strict=True):
        p = "ip ip-prefix %s permit %%s" % name
        if not strict:
            p += " le 32"
        return "undo ip ip-prefix %s\n" % name + "\n".join([p % x.replace("/", " ") for x in pl])

<<<<<<< HEAD
    rx_interface_name = re.compile(
        r"^(?P<type>Eth|[A-Z]+E|Vlan)(?P<number>[\d/]+)$"
    )
=======
    rx_interface_name = re.compile(r"^(?P<type>[A-Z]+E)(?P<number>[\d/]+)$")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("GE2/0/0")
        'GigabitEthernet2/0/0'
        """
        match = self.rx_interface_name.match(s)
        if not match:
            return s
<<<<<<< HEAD
        return "%s%s" % (
            {
                "GE": "GigabitEthernet",
                "Eth": "Ethernet",
                "Vlan": "Vlan-interface"
            }[match.group("type")], match.group("number")
        )

    convert_mac = BaseProfile.convert_mac_to_huawei

    spaces_rx = re.compile("^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)

    def clean_spaces(self, config):
        config = self.spaces_rx.sub("", config)
=======
        return "%s%s" % ({"GE": "GigabitEthernet"}[match.group("type")], match.group("number"))

    def clean_spaces(self, config):
        rx = re.compile("^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)
        config = rx.sub("", config)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return config
