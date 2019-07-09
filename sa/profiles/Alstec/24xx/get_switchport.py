# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    name = "Alstec.24xx.get_switchport"
    cache = True
    interface = IGetSwitchport

    rx_vlan = re.compile(
        r"^interface (?P<port>\d+/\d+)\s*\n"
        r"(?:^no.+\n)*(^vlan pvid (?P<pvid>\d+)\s*$)?"
        r"(^vlan tagging (?P<tagged>\S+)\s*$)?",
        re.MULTILINE,
    )
    rx_split = re.compile(r"^interface (?P<port>\d+/\d+)\s*$", re.MULTILINE)
    rx_pvid = re.compile(r"vlan pvid (?P<pvid>\d+)\s*")
    rx_tagged = re.compile(r"vlan tagging (?P<tagged>\S+)\s*")

    def execute_cli(self):
        r = []
        c = self.scripts.get_config()
        ne = self.rx_split.split(c)
        for n in range(1, len(ne), 2):
            iface, body = ne[n : n + 2]
            r += [{"interface": iface, "tagged": [], "members": []}]
            if self.rx_pvid.search(body):
                r[-1]["untagged"] = self.rx_pvid.search(body).group("pvid")
            if self.rx_tagged.search(body):
                r[-1]["tagged"] = self.expand_rangelist(self.rx_tagged.search(body).group("tagged"))
        return r
