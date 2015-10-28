# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_interface_index
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetIfIndex
import re


class Script(BaseScript):
    name = "Cisco.IOS.get_interface_index"
    interface = IGetIfIndex
    rx_line = re.compile(
        r"Interface = \S+, Ifindex = (?P<index>\d+)")

    def execute(self, interface):
        try:
            c = self.cli("show snmp mib ifmib ifindex %s" % interface)
        except self.CLISyntaxError:
            return None

        match = self.re_search(self.rx_line, c)
        if match:
            return int(match.group("index"))
        return None
