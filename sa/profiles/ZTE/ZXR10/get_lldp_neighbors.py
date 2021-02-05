# ---------------------------------------------------------------------
# ZTE.ZXR10.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    # LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    # LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    # LLDP_PORT_SUBTYPE_ALIAS,
    # LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    # LLDP_PORT_SUBTYPE_LOCAL,
)
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "ZTE.ZXR10.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    kv_map = {
        "local port": "port",
        "chassis id": "chassis",
        "port id": "remote_port",
        "port description": "remote_description",
        "system name": "sysname",
    }

    port_subtype = {
        "mac address": LLDP_PORT_SUBTYPE_MAC,
        "interface name": LLDP_PORT_SUBTYPE_NAME,
    }

    chassis_subtype = {"mac address": LLDP_CHASSIS_SUBTYPE_MAC}

    rx_lldp_subtype = re.compile(r"(?P<value>.+)\s\((?P<type>.+)\)\s*$")

    rx_splitter = re.compile("^-+")

    def execute_cli(self):
        result = []
        v = self.cli("show lldp entry")
        for entry in self.rx_splitter.split(v):
            if not entry:
                continue
            r = parse_kv(self.kv_map, entry)

            remote_port_match = self.rx_lldp_subtype.match(r["remote_port"])
            if not remote_port_match:
                self.logger.warning("Unknown remote port_id format: %s", r["remote_port"])
                continue

            remote_match = self.rx_lldp_subtype.match(r["chassis"])
            if not remote_match:
                self.logger.warning("Unknown remote chassis format: %s", r["chassis"])
                continue
            chassis_id, chassis_subtype = remote_match.groups()
            remote_port, remote_port_type = remote_port_match.groups()
            if chassis_subtype.lower() == "mac address":
                chassis_id = chassis_id.replace(".", ":")

            neighbor = {
                "remote_chassis_id_subtype": self.chassis_subtype[chassis_subtype.lower()],
                "remote_chassis_id": chassis_id,
                "remote_port_subtype": self.port_subtype[remote_port_type.lower()],
                "remote_port": remote_port,
            }
            if "remote_description" in r:
                neighbor["remote_port_description"] = r["remote_description"]
            if "sysname" in r:
                neighbor["remote_system_name"] = r["sysname"]
            result += [{"local_interface": r["port"], "neighbors": [neighbor]}]
        return result
