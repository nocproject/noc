# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetInterfaceStatus
import re


class Script(BaseScript):
    name = "OS.FreeBSD.get_interface_status"
    interface = IGetInterfaceStatus
    rx_if_name = re.compile(
        r"^(?P<ifname>\S+): flags=\d+<\S+> metric \d+ mtu \d+$")
    rx_if_status = re.compile(
        r"^\tstatus: "
        r"(?P<status>active|no carrier|inserted|no ring|associated|running)$")

    def execute(self):
        r = []
        for s in self.cli("ifconfig -v", cached=True).splitlines():
            match = self.rx_if_name.search(s)
            if match:
                if_name = match.group("ifname")
                continue
            match = self.rx_if_status.search(s)
            if match:
                r += [{
                    "interface": if_name,
                    "status": not match.group("status").startswith("no ")
                }]
                continue
        return r
