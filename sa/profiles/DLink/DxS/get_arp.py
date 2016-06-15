# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "DLink.DxS.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)\s+\S+\s*$", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        for match in self.rx_line.finditer(self.cli("show arpentry")):
            if match.group("mac") == "FF-FF-FF-FF-FF-FF":
                continue
            if (interface is not None) \
            and (interface != match.group("interface")):
                continue
            r.append(match.groupdict())
        return r
