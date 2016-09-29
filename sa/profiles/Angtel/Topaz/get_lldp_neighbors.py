# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Angtel.Topaz.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4, is_ipv6
from noc.lib.mac import MAC


class Script(BaseScript):
    name = "Angtel.Topaz.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+(?P<system_id>\S+)\s+"
        r"(?P<port_id>\S+)\s+(?P<system_name>.*)\s+(?P<caps>\S+)\s+\d+",
        re.IGNORECASE)

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for l in v.split("\n"):
            match = self.rx_line.search(l)
            if match:
                chassis_id = match.group("system_id")
                if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                    chassis_id_subtype = 5
                else:
                    try:
                        MACAddressParameter().clean(chassis_id)
                        chassis_id_subtype = 4
                    except ValueError:
                        chassis_id_subtype = 7
                port_id = match.group("port_id")
                if is_ipv4(port_id) or is_ipv6(port_id):
                    port_id_subtype = 4
                else:
                    try:
                        MACAddressParameter().clean(port_id)
                        port_id_subtype = 3
                    except ValueError:
                        port_id_subtype = 7
                caps = 0
                if "O" in match.group("caps"):
                    caps += 1
                elif "r" in match.group("caps"):
                    caps += 2
                elif "B" in match.group("caps"):
                    caps += 4
                elif "W" in match.group("caps"):
                    caps += 8
                elif "R" in match.group("caps"):
                    caps += 16
                elif "T" in match.group("caps"):
                    caps += 32
                elif "D" in match.group("caps"):
                    caps += 64
                elif "H" in match.group("caps"):
                    caps += 128
                neighbor = {
                    "remote_chassis_id": chassis_id,
                    "remote_chassis_id_subtype": chassis_id_subtype,
                    "remote_port": port_id,
                    "remote_port_subtype": port_id_subtype,
                    "remote_capabilities": caps
                }
                if match.group("system_name"):
                    neighbor["remote_system_name"] = match.group("system_name")
                r += [{
                    "local_interface": match.group("port"),
                    "neighbors": [neighbor]
                }]
        return r