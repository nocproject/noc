# ---------------------------------------------------------------------
# HP.Comware.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_CHASSIS_COMPONENT,
    LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_AGENT_CIRCUIT_ID,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_NAMES,
    lldp_caps_to_bits,
)
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "HP.Comware.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    lldp_kv_map = {
        "neighbor index": "neighbor_index",
        "lldp neighbor index": "neighbor_index",
        "update time": "update_time",
        "chassis type": "remote_chassis_id_subtype",
        "chassis id": "remote_chassis_id",
        "port id type": "remote_port_subtype",
        "port id": "remote_port",
        "port description": "remote_port_description",
        "system name": "remote_system_name",
        "system description": "remote_system_description",
        "system capabilities supported": "remote_capabilities",
        "capabilities": "remote_capabilities",
        "chassisid/subtype": "remote_chassis_id_type",
        "portid/subtype": "remote_port_type",
    }

    rx_lldp_neighbor_split = re.compile(r"LLDP neighbor-information of port")

    rx_local_port = re.compile(r"^\s*\d+\[(?P<interface>\S+)\]\:")

    chassis_type_map = {
        "chassis component": LLDP_CHASSIS_SUBTYPE_CHASSIS_COMPONENT,
        "interface alias": LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
        "port component": LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
        "mac address": LLDP_CHASSIS_SUBTYPE_MAC,
        "network address": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
        "network address(ipv4)": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
        "interface name": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
        "local": LLDP_CHASSIS_SUBTYPE_LOCAL,
    }

    port_type_map = {
        "interface alias": LLDP_PORT_SUBTYPE_ALIAS,
        "port component": LLDP_PORT_SUBTYPE_COMPONENT,
        "mac address": LLDP_PORT_SUBTYPE_MAC,
        "network address": LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
        "network address(ipv4)": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
        "interface name": LLDP_PORT_SUBTYPE_NAME,
        "agent circuit id": LLDP_PORT_SUBTYPE_AGENT_CIRCUIT_ID,
        "locally assigned": LLDP_PORT_SUBTYPE_LOCAL,
    }

    def execute_cli(self, **kwargs):
        result = []
        try:
            v = self.cli("display lldp neighbor-information")
        except self.CLISyntaxError:
            return []
        for nei in self.rx_lldp_neighbor_split.split(v):
            if not nei.strip():
                continue
            match = self.rx_local_port.search(nei)
            if not match:
                self.logger.info("Not find local port")
                continue
            n = {}
            r = parse_kv(self.lldp_kv_map, nei)
            if "remote_chassis_id_subtype" in r:
                n["remote_chassis_id_subtype"] = r["remote_chassis_id_subtype"]
            if "remote_chassis_id_type" in r:
                n["remote_chassis_id"], n["remote_chassis_id_subtype"] = r[
                    "remote_chassis_id_type"
                ].rsplit("/", 1)
            if "remote_chassis_id" in r:
                n["remote_chassis_id"] = r["remote_chassis_id"]
            if "remote_chassis_id" not in n:
                self.logger.warning(
                    "[%s] Not found remote chassis id on output", match.group("interface")
                )
                continue
            n["remote_chassis_id_subtype"] = self.chassis_type_map[
                n["remote_chassis_id_subtype"].lower()
            ]
            # Port fields
            if "remote_port_subtype" in r:
                n["remote_port_subtype"] = r["remote_port_subtype"]
            if "remote_port_type" in r:
                n["remote_port"], n["remote_port_subtype"] = r["remote_port_type"].rsplit("/", 1)
            if "remote_port" in r:
                n["remote_port"] = r["remote_port"]
            if "remote_port" not in n:
                self.logger.warning("[%s] Not found port id on output", match.group("interface"))
                continue
            n["remote_port_subtype"] = self.port_type_map[n["remote_port_subtype"].lower()]
            if "remote_system_description" in r:
                n["remote_system_description"] = r["remote_system_description"].strip()
            if "remote_capabilities" in r:
                n["remote_capabilities"] = lldp_caps_to_bits(
                    [x.strip() for x in r["remote_capabilities"].split(",")],
                    {LLDP_CAP_NAMES[x1]: x1 for x1 in LLDP_CAP_NAMES},
                )
            result += [{"local_interface": match.group("interface"), "neighbors": [n]}]
        return result
