# ---------------------------------------------------------------------
# Eltex.LTE.get_interface_status
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
    name = "Eltex.LTE.get_interface_status"
    interface = IGetInterfaceStatus
    cache = True

    rx_port = re.compile(r"^(?P<interface>\d+)\s+(?P<status>up|down)\s+", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        with self.profile.switch(self):
            cmd = self.cli("show ports", cached=True)
            for match in self.rx_port.finditer(cmd):
                if interface is not None and interface == match.group("interface"):
                    return [
                        {
                            "interface": match.group("interface"),
                            "status": match.group("status") == "up",
                        }
                    ]
                r += [
                    {
                        "interface": match.group("interface"),
                        "status": match.group("status") == "up",
                    }
                ]
        return r
