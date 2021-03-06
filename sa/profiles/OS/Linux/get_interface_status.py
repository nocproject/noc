# ---------------------------------------------------------------------
# OS.Linux.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "OS.Linux.get_interface_status"
    interface = IGetInterfaceStatus

    rx_if_name = re.compile(r"^(?P<ifname>\S+)\s+Link encap:")
    rx_if_status = re.compile(r"^\s+UP+(\s|BROADCAST\s)+(?P<status>.+)+\s")

    def execute(self, interface=None):
        r = []
        s = self.cli("ifconfig").split("\n")
        for i in range(len(s)):
            ln = s[i]
            match = self.rx_if_name.search(ln)
            if match:
                if_name = match.group("ifname")
                if interface:
                    if if_name == interface:
                        i += 1
                        ln = s[i]
                        while ln.strip()[:4] == "inet":
                            i += 1
                            ln = s[i]
                        status = self.rx_if_status.search(ln)
                        if status:
                            r = [
                                {
                                    "interface": if_name,
                                    "status": "RUNNING" in status.group("status"),
                                }
                            ]
                elif "." not in if_name and (if_name[:3] == "eth" or if_name[:3] == "ath"):
                    i += 1
                    ln = s[i]
                    while ln.strip()[:4] == "inet":
                        i += 1
                        ln = s[i]
                    status = self.rx_if_status.search(ln)
                    if status:
                        r += [{"interface": if_name, "status": "RUNNING" in status.group("status")}]
        if not r:
            raise Exception("Not implemented")
        return r
