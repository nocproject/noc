# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
import re


class Script(NOCScript):
    name = "OS.FreeBSD.get_interface_status"
    implements = [IGetInterfaceStatus]
    rx_if_name = re.compile(
    r"^(?P<ifname>\S+): flags=\d+<\S+> metric \d+ mtu \d+$")
    rx_if_status = re.compile(r"^\tstatus: (?P<status>active|no carrier)$")

    def execute(self):
        r = []
        for s in self.cli("ifconfig", cached=True).splitlines():
            match = self.rx_if_name.search(s)
            if match:
                if_name = match.group("ifname")
                continue
            match = self.rx_if_status.search(s)
            if match:
                r += [{
                    "interface": if_name,
                    "status": match.group("status") == "active"
                }]
                continue
        return r
