# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Arista.EOS.get_interface_status"
    interface = IGetInterfaceStatus

    rx_interface_status = re.compile(
        r"^(?P<interface>\S\S\d+).+?"
        r"(?P<status>connected|notconnect)"
    )

    def execute(self, interface=None):
        r = []
        v = self.cli("show interfaces status")
        for l in v.splitlines():
            match = self.rx_interface_status.match(l)
            if match:
                r += [{
                    "interface": match.group("interface"),
                    "status": match.group("status") == "connected"
                }]
        return r
