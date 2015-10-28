# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Qtech.QSW2800.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_int = re.compile(r"^Port name\s+:\s+(?P<interface>.+)\n"
                        r"Port Remote Counter\s+:\s+(?P<count>\d+)\n"
                        r"TimeMark\s+:\d+\n"
                        r"ChassisIdSubtype\s+:(?P<chassis_subtype>\d+)\n"
                        r"ChassisId\s+:(?P<chassis_id>.+)\n"
                        r"PortIdSubtype\s+:(?P<port_subtype>.+)\n"
                        r"PortId\s+:(?P<port_id>.+)\n",
                        re.MULTILINE)

    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute(self):
        result = []
        try:
            lldp = self.cli("show lldp neighbors interface")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        for match in self.rx_int.finditer(lldp):
            if match.group("count") == 0:
                continue
            result += [{
                "local_interface": match.group("interface"),
                "neighbors": [{
                    "remote_chassis_id_subtype": match.group("chassis_subtype"),
                    "remote_chassis_id": match.group("chassis_id"),
                    "remote_port_subtype": {
                        "Local": 7,
                        "Interface": 5,
                        "MAC address": 3
                    }[match.group("port_subtype")],
                    "remote_port": match.group("port_id")
                }]
            }]
        return result
