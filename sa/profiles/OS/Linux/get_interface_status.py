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
    rx_if_status = re.compile(r"^\s+UP+\s+(?P<status>.+)+\s+MTU:+\d+\s+Metric:+\d+")

    def execute(self):
        r = []
        for s in self.cli("ifconfig").split('\n'):
            match = self.rx_if_name.search(s)
            if match:
                if_name = match.group("ifname")
                continue
            match = self.rx_if_status.search(s)
            if match:
                r += [{
                    "interface" : if_name,
                    "status"    : 'RUNNING' in match.group("status"),
                    }]
                continue
        if not r:
            raise Exception("Not implemented")
        return r
