# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "3Com.SuperStack3.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)\s+\S+\s*$", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        cmd = "protocol ip arp"
        if interface is not None:
            cmd += " find %s" % interface
        else:
            cmd += " detail all"
        for match in self.rx_line.finditer(self.cli(cmd)):
            mac = match.group("mac")
            interface = match.group("interface")
            if mac.lower() == "ff-ff-ff-ff-ff-ff":
                continue
            if not interface.startswith("1:"):
                interface = "1:" + interface
            r += [{
                "interface": interface,
                "ip": match.group("ip"),
                "mac": mac
            }]
        return r
