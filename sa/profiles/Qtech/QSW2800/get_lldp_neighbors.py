# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors


class Script(NOCScript):
    name = "Qtech.QSW2800.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_int = re.compile(r"^Port name\s+:\s+(?P<interface>\S+)."
                r"Port Remote Counter\s+:\s+(?P<count>\d+).TimeMark\s+:\d+."
                r"ChassisIdSubtype\s+:(?P<chassis_subtype>\d+)."
                r"ChassisId\s+:(?P<chassis_id>\S+)."
                r"PortIdSubtype\s+:(?P<port_subtype>\S+)."
                r"PortId\s+:(?P<port_id>\S+).",
                re.MULTILINE | re.DOTALL)

    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute(self):
        r = []
        try:
            lldp = self.cli("show lldp neighbors interface")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        for match in self.rx_int.finditer(lldp):
            if match.group("count") == 0:
                continue
            r += [{
                "local_interface": match.group("interface"),
                "neighbors": [{
                    "remote_chassis_id_subtype": match.group("chassis_subtype"),
                    "remote_chassis_id": match.group("chassis_id"),
                    "remote_port_subtype": {
                        "Local": 7,
                        "Interface": 5
                    }[match.group("port_subtype")],
                    "remote_port": match.group("port_id")
                }]
            }]
        return r
