# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors, MACAddressParameter
from noc.lib.text import parse_kv


class Script(NOCScript):
    name = "Huawei.VRP.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    @NOCScript.match(version__startswith="3.")
    def execute_vrp3(self):
        """
        No LLDP on VRP3
        :return:
        """
        raise self.NotSupportedError()

    rx_iface_sep = re.compile(
        r"^(\S+)\s+has\s+\d+\s+neighbors", re.MULTILINE
    )

    rx_neighbor_split = re.compile(
        r"^Neighbor index\s*:\s+\d+",
        re.MULTILINE
    )

    CHASSIS_TYPES = {
        "macaddress": 4,
        "interfacename": 6,
        "local": 7
    }

    PORT_TYPES = {
        "interfacealias": 1,
        "macaddress": 3,
        "interfacename": 5,
        "local": 7
    }

    CAPS = {
        "NA": 0, "other": 1, "repeater": 2, "bridge": 4,
        "WLAN": 8, "router": 16, "telephone": 32,
        "cable": 64, "station": 128
    }

    @NOCScript.match()
    def execute_other(self):
        """
        VRP5 style
        :return:
        """
        r = []
        try:
            v = self.cli("display lldp neighbor")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        il = self.rx_iface_sep.split(v)[1:]
        for local_iface, data in zip(il[::2], il[1::2]):
            neighbors = []
            for ndata in self.rx_neighbor_split.split(data)[1:]:
                n = parse_kv({
                    "chassis type": "remote_chassis_id_subtype",
                    "chassis id": "remote_chassis_id",
                    "port id type": "remote_port_subtype",
                    "port id": "remote_port",
                    "system capabilities enabled": "remote_capabilities",
                    "system name": "remote_system_name"
                }, ndata)
                # Convert chassis id
                n["remote_chassis_id_subtype"] = self.CHASSIS_TYPES[n["remote_chassis_id_subtype"].lower()]
                if n["remote_chassis_id_subtype"] == 3:
                    n["remote_chassis_id"] = MACAddressParameter().clean(n["remote_chassis_id"])
                # Convert port id
                n["remote_port_subtype"] = self.PORT_TYPES[n["remote_port_subtype"].lower()]
                if n["remote_port_subtype"] == 3:
                    n["remote_port"] = MACAddressParameter().clean(n["remote_port"])
                # Process capabilities
                caps = 0
                for c in n.get("remote_capabilities", "").split(","):
                    caps |= self.CAPS[c.strip()]
                n["remote_capabilities"] = caps
                neighbors += [n]
            if neighbors:
                r += [{
                    "local_interface": local_iface,
                    "neighbors": neighbors
                }]
        return r
