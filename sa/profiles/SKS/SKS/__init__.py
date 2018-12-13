# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: SKS (SVYAZKOMPLEKTSERVICE, LLC. - http://skss.ru/)
# OS:     SKS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "SKS.SKS"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = \
        r"% Unrecognized command|% Wrong number of parameters|" \
        r"% Unrecognized host or address|" \
        r"Unknown command|Incomplete command|Too many parameters"
    command_super = "enable"
    command_disable_pager = "terminal datadump"
    pattern_more = [
        ("More: <space>,  Quit: q or CTRL+Z, One line: <return>", "a"),
        ("^ --More-- ", " ")
    ]
    config_volatile = [
        r"enable password 7 \S+( level \d+)?\n",
        r"username \S+ password 7 \S+( author\-group \S+)?\n",
        r"radius(-server | accounting-server )(encrypt-key|key) \d+ \S+\n",
        r"tacacs(-server | accounting-server )(encrypt-key|key) \d+ \S+\n"
    ]

    rx_iface = re.compile("^[fgvn]\d+\S*$")

    def convert_interface_name(self, interface):
        if bool(self.rx_iface.search(interface)):
            if interface.startswith("f"):
                return "FastEthernet" + interface[1:]
            if interface.startswith("g"):
                return "GigaEthernet" + interface[1:]
            if interface.startswith("v"):
                return "VLAN" + interface[1:]
            if interface.startswith("n"):
                return "Null" + interface[1:]
        return interface
