# ---------------------------------------------------------------------
# HP.Aruba.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter, IPv4Parameter
from noc.core.validators import is_int, is_ipv4, is_ipv6, is_mac
from noc.core.text import parse_kv
from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    # LLDP_CAP_OTHER,
    # LLDP_CAP_REPEATER,
    # LLDP_CAP_BRIDGE,
    # LLDP_CAP_WLAN_ACCESS_POINT,
    # LLDP_CAP_ROUTER,
    # LLDP_CAP_TELEPHONE,
    # LLDP_CAP_DOCSIS_CABLE_DEVICE,
    # LLDP_CAP_STATION_ONLY,
    # lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "HP.Aruba.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_nei_splitter = re.compile(r"----+\n", re.MULTILINE)
    rx_port_nei_splitter = re.compile(r"\n\nNeighbor System-Name")
    parse_kv_map = {
        "port": "local_interface",
        "neighbor chassis-name": "remote_system_name",
        "neighbor chassis-description": "remote_system_description",
        "neighbor chassis-id": "remote_chassis_id",
        "neighbor management-address": "remote_mgmt_address",
        "neighbor system-name": "remote_system_name",
        "neighbor port-id": "remote_port",
        "port-id": "remote_port",
        "neighbor port-desc": "remote_port_description",
    }

    def parse_port_neighbor(self, nei: str):
        nei = parse_kv(self.parse_kv_map, nei.strip())
        remote_port = nei["remote_port"]
        remote_port_subtype = LLDP_PORT_SUBTYPE_ALIAS
        if is_ipv4(remote_port):
            remote_port = IPv4Parameter().clean(remote_port)
            remote_port_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
        elif is_mac(remote_port):
            # Convert MAC to common form
            remote_port = MACAddressParameter().clean(remote_port)
            remote_port_subtype = LLDP_PORT_SUBTYPE_MAC
        elif is_int(remote_port):
            remote_port_subtype = LLDP_PORT_SUBTYPE_LOCAL
        n = {
            "remote_port": remote_port,
            "remote_port_subtype": remote_port_subtype,
            "remote_chassis_id_subtype": LLDP_CHASSIS_SUBTYPE_MAC,
            "remote_chassis_id": nei["remote_chassis_id"],
        }
        # Get capabilities
        # cap = 0
        # match = self.rx_enabled_caps.search(v)
        # if match:
        #     cap = lldp_caps_to_bits(
        #         match.group("caps").strip().split(","),
        #         {
        #             "o": LLDP_CAP_OTHER,
        #             "p": LLDP_CAP_REPEATER,
        #             "b": LLDP_CAP_BRIDGE,
        #             "w": LLDP_CAP_WLAN_ACCESS_POINT,
        #             "r": LLDP_CAP_ROUTER,
        #             "t": LLDP_CAP_TELEPHONE,
        #             "c": LLDP_CAP_DOCSIS_CABLE_DEVICE,
        #             "s": LLDP_CAP_STATION_ONLY,
        #         },
        #     )
        # n["remote_capabilities"] = cap
        # Get remote chassis id
        if "remote_port_description" in nei:
            n["remote_port_description"] = nei["remote_port_description"]
        if "remote_system_name" in nei:
            n["remote_system_name"] = nei["remote_system_name"]
        if nei.get("remote_mgmt_address") and is_ipv4(nei["remote_mgmt_address"]):
            n["remote_mgmt_address"] = nei["remote_mgmt_address"]
        if is_ipv4(n["remote_chassis_id"]) or is_ipv6(n["remote_chassis_id"]):
            n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
        elif is_mac(n["remote_chassis_id"]):
            pass
        else:
            n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_LOCAL
        return n

    def execute_cli(self):
        try:
            v = self.cli("show lldp neighbor-info detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        neighbors = defaultdict(list)  # Neighbor -> data map
        for li in self.rx_nei_splitter.split(v):
            port = parse_kv({"port": "local_interface", "neighbor entries": "neighbors_count"}, li)
            # for nn in li.split("\n\n"):
            nei = parse_kv(self.parse_kv_map, li.strip())
            if not nei:
                continue
            if int(port["neighbors_count"]) == 0:
                continue
            elif int(port["neighbors_count"]) == 1:
                neighbors[port["local_interface"]].append(self.parse_port_neighbor(li))
                continue
            # Multiple entries
            self.logger.warning(
                "[%s] Multiple neighbors: %s",
                port["local_interface"],
                port["neighbors_count"],
            )
            r = self.rx_port_nei_splitter.split(li)
            neighbors[port["local_interface"]].append(self.parse_port_neighbor(r[0]))
            for nei in r[1:]:
                neighbors[port["local_interface"]].append(
                    self.parse_port_neighbor("Neighbor System-Name" + nei)
                )
        return [{"local_interface": li, "neighbors": neighbors[li]} for li in neighbors]
