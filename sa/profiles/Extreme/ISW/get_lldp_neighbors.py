# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.ISW.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.text import parse_kv
from noc.core.validators import is_mac
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_LOCAL,
)


class Script(BaseScript):
    name = "Extreme.ISW.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    lldp_map = {
        "local interface": "local_interface",
        "chassis id": "remote_chassis_id",
        "port id": "remote_port",
        "port description": "remote_port_description",
        "system name": "remote_system_name",
        "system description": "remote_system_description",
    }

    def execute_cli(self, **kwargs):
        r = []
        try:
            lldp = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise NotImplementedError

        for block in lldp.split("\n\n"):
            neighbors = []
            if not block:
                continue
            n = parse_kv(self.lldp_map, block)
            loca_iface = n.pop("local_interface")
            if is_mac(n["remote_chassis_id"]):
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_LOCAL
            if is_mac(n["remote_port"]):
                n["remote_port_subtype"] = LLDP_PORT_SUBTYPE_MAC
            else:
                n["remote_port_subtype"] = LLDP_PORT_SUBTYPE_LOCAL

            neighbors += [n]
            if neighbors:
                r += [{"local_interface": loca_iface, "neighbors": neighbors}]
        return r
