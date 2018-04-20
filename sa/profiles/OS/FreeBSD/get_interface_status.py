# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# OS.FreeBSD.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
import re


class Script(BaseScript):
    name = "OS.FreeBSD.get_interface_status"
    interface = IGetInterfaceStatus
    rx_if_name = re.compile(
        r"^(?P<ifname>\S+): flags=[0-9a-f]+<\S+> metric \d+ mtu \d+$")

=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_if_status = re.compile(
        r"^\tstatus: "
        r"(?P<status>active|no carrier|inserted|no ring|associated|running)$")

<<<<<<< HEAD
    def execute(self, interface=None):
=======
    def execute(self):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        r = []
        for s in self.cli("ifconfig -v", cached=True).splitlines():
            match = self.rx_if_name.search(s)
            if match:
                if_name = match.group("ifname")
                continue
            match = self.rx_if_status.search(s)
            if match:
<<<<<<< HEAD
                iface = {
                    "interface": if_name,
                    "status": not match.group("status").startswith("no ")
                }
                if (interface is not None) and (interface == if_name):
                    return [iface]
                r += [iface]
=======
                r += [{
                    "interface": if_name,
                    "status": not match.group("status").startswith("no ")
                }]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                continue
        return r
