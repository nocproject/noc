# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: D-Link
# OS:     DAS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DAS"
    pattern_syntax_error = r"(Error: Invalid command)"
    pattern_prompt = r"(?P<hostname>\S*)[#$]"
    command_exit = "logout"
    config_volatile = ["^%.*?$"]
    telnet_naws = b"\x00\x7f\x00\x7f"
    snmp_metrics_get_chunk = 10

    matchers = {"is_vendor_conexant": {"version": {"$regex": r"^D.+"}}}

    base_indexes = {
        "lo": 0,
        "eth": 1,  # 1-3
        "veth": 4,  # 4-5
        "dsl": 6,  # 6-53
        "atm": 150,  # 150-197
        "aal5": 198,  # 198-581
        "ppp": 582,  # 582
        "eoa": 391,  # 391-774
        "dsli": 54,  # 54-101
        "dslf": 102,  # 102-149
    }
    rx_ifname = re.compile(r"^(?P<ifname>\w+)-(?P<ifnum>\d+)?")

    def get_ifindexes(self, name):
        match = self.rx_ifname.match(name)
        if not match:
            return None
        return self.base_indexes[match.group("ifname")] + int(match.group("ifnum"))
