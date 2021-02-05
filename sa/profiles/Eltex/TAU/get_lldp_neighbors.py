# ---------------------------------------------------------------------
# Eltex.TAU.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.text import parse_kv
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
)


class Script(BaseScript):
    name = "Eltex.TAU.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    lldp_map = {
        "interface": "local_interface",
        "chassisid": "remote_chassis_id",
        "sysname": "remote_system_name",
        "sysdescr": "remote_system_description",
        "portid": "remote_port",
        "portdescr": "remote_port_description",
        "capability": "remote_capabilities",
    }

    def execute_cli(self, **kwargs):
        r = []
        try:
            lldp = self.cli("lldpctl", cached=True)
        except self.CLISyntaxError:
            return []

        for block in lldp.split("----"):
            neighbors = []
            if not block:
                continue
            n = parse_kv(self.lldp_map, block)
            if not n:
                continue
            n["local_interface"] = n["local_interface"].split(",")[0]
            loca_iface = n.pop("local_interface")
            if n["remote_chassis_id"].startswith("mac"):
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_MAC
            elif n["remote_chassis_id"].startswith("ifname"):
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME
            else:
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_LOCAL
            n["remote_chassis_id"] = n["remote_chassis_id"].split(" ")[1]
            if n["remote_port"].startswith("mac"):
                n["remote_port_subtype"] = LLDP_PORT_SUBTYPE_MAC
            elif n["remote_port"].startswith("ifname"):
                n["remote_port_subtype"] = LLDP_PORT_SUBTYPE_NAME
            else:
                n["remote_port_subtype"] = LLDP_PORT_SUBTYPE_LOCAL
            n["remote_capabilities"] = 0
            n["remote_port"] = n["remote_port"].split(" ")[1]
            neighbors += [n]
            if neighbors:
                r += [{"local_interface": loca_iface, "neighbors": neighbors}]
        return r
