# ---------------------------------------------------------------------
# Orion.NOS.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Orion.NOS.get_interface_status"
    interface = IGetInterfaceStatus

    rx_port = re.compile(r"^\s*P?(?P<port>\d+)\s+\S+\s+(?P<oper_status>\S+)", re.MULTILINE)

    def execute_cli(self, interface=None):
        r = []
        if self.is_beta:
            port_count = self.profile.get_port_count(self)
            c = self.cli(("show interface port-list 1-%d" % port_count), cached=True)
            for match in self.rx_port.finditer(c):
                if (interface is not None) and (interface == match.group("port")):
                    return [
                        {
                            "interface": match.group("port"),
                            "status": "down" not in match.group("oper_status"),
                        }
                    ]
                r += [
                    {
                        "interface": match.group("port"),
                        "status": "down" not in match.group("oper_status"),
                    }
                ]
            return r

        for match in self.rx_port.finditer(self.cli("show interface port")):
            if (interface is not None) and (interface == match.group("port")):
                return [
                    {
                        "interface": match.group("port"),
                        "status": match.group("oper_status") != "down",
                    }
                ]
            r += [
                {"interface": match.group("port"), "status": match.group("oper_status") != "down"}
            ]
        return r
