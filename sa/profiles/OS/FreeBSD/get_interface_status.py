# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OS.FreeBSD.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "OS.FreeBSD.get_interface_status"
    interface = IGetInterfaceStatus
    rx_if_name = re.compile(
        r"^(?P<ifname>\S+): flags=[0-9a-f]+<\S+> metric \d+ mtu \d+$")

    rx_if_status = re.compile(
        r"^\tstatus: "
        r"(?P<status>active|no carrier|inserted|no ring|associated|running)$")

    def execute(self, interface=None):
        r = []
        for s in self.cli("ifconfig -v", cached=True).splitlines():
            match = self.rx_if_name.search(s)
            if match:
                if_name = match.group("ifname")
                continue
            match = self.rx_if_status.search(s)
            if match:
                iface = {
                    "interface": if_name,
                    "status": not match.group("status").startswith("no ")
                }
                if (interface is not None) and (interface == if_name):
                    return [iface]
                r += [iface]
                continue
        return r
