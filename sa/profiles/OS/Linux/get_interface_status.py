# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus


class Script(NOCScript):
    name = "OS.Linux.get_interface_status"
    implements = [IGetInterfaceStatus]

    rx_if_name = re.compile(r"^(?P<ifname>\S+)\s+Link encap:")
    rx_if_status = re.compile(r"^\s+UP+(\s|BROADCAST\s)+(?P<status>.+)+\s")

    def execute(self, interface=None):
        r = []
        s = self.cli("ifconfig").split('\n')
        for i in range(len(s)):
            l = s[i]
            match = self.rx_if_name.search(l)
            if match:
                if_name = match.group("ifname")
                if interface:
                    if if_name == interface:
                        i += 1
                        l = s[i]
                        while l.strip()[:4] == 'inet':
                            i += 1
                            l = s[i]
                        status = self.rx_if_status.search(l)
                        if status:
                            r = [{
                                "interface": if_name,
                                "status": 'RUNNING' in status.group("status"),
                                }]
                elif '.' not in if_name and (if_name[:3] == 'eth' or\
                        if_name[:3] == 'ath'):
                    i += 1
                    l = s[i]
                    while l.strip()[:4] == 'inet':
                        i += 1
                        l = s[i]
                    status = self.rx_if_status.search(l)
                    if status:
                        r += [{
                            "interface": if_name,
                            "status": 'RUNNING' in status.group("status"),
                            }]
        if not r:
            raise Exception("Not implemented")
        return r
