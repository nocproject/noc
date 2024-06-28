# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import IntParameter, MACAddressParameter, InterfaceTypeError
from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
)


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_detail = re.compile(
        r"^(?P<local_if>\S+)\s+(?P<id>\S+)\s+(?P<rem_cid_type>\d+)\s+(?P<port_id>\S+)\s+(?P<p_type>Local|Interface|MAC address)",
        re.MULTILINE,
    )

    def execute_cli(self, **kwargs):
        r = []
        # Fallback to CLI
        for lldp in self.cli("show lldp neighbors brief").split('\n'):
            match = self.rx_detail.search(lldp)
            if match:
                i = {"local_interface": match.group("local_if"), "neighbors": []}
                n = {"remote_chassis_id_subtype": match.group("rem_cid_type")}
                n["remote_port_subtype"] = {
                    "Interface alias": LLDP_PORT_SUBTYPE_ALIAS,
                    # "Port component": 2,
                    "MAC address": LLDP_PORT_SUBTYPE_MAC,
                    "Interface": LLDP_PORT_SUBTYPE_NAME,
                    "Local": LLDP_PORT_SUBTYPE_LOCAL,
                }[match.group("p_type")]
                if n["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC:
                    remote_port = MACAddressParameter().clean(match.group("port_id"))
                elif n["remote_port_subtype"] == LLDP_PORT_SUBTYPE_LOCAL:
                    p_id = match.group("port_id")
                    try:
                        remote_port = IntParameter().clean(p_id)
                    except InterfaceTypeError:
                        remote_port = p_id
                else:
                    remote_port = match.group("port_id")
                n["remote_chassis_id"] = match.group("id")
                n["remote_port"] = str(remote_port)
                # Get capability
                cap = 0
                n["remote_capabilities"] = cap
                i["neighbors"] += [n]
                r += [i]
        return r
