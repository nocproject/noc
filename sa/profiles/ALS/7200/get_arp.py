# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ALS.7200.get_arp
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
    name = "ALS.7200.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<interface>\S+)\s*", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp switch")):
            if (interface is not None) \
            and (interface != match.group("interface")):
                continue
            r.append(match.groupdict())
        return r
