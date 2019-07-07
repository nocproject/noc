# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_ROUTER,
    LLDP_CAP_STATION_ONLY,
    LLDP_CAP_WLAN_ACCESS_POINT,
)


class Script(BaseScript):
    name = "Eltex.ESR.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_neighbor = re.compile(r"^(?P<local_interface>gi\d+/\d+/\d+)\s+", re.MULTILINE)
    rx_detail = re.compile(
        r"^\s*Index:\s+\d+\s*\n"
        r"^\s*Local Interface:\s+\S+\s*\n"
        r"^\s*Chassis type:\s+(?P<chassis_id_type>.+)\s*\n"
        r"^\s*Chassis ID:\s+(?P<chassis_id>\S+)\s*\n"
        r"^\s*Port type:\s+(?P<port_id_type>.+)\s*\n"
        r"^\s*Port ID:\s+(?P<port_id>\S+)\s*\n"
        r"^\s*Port description:(?P<port_descr>.*)\n"
        r"^\s*Time to live:\s+\d+\s*\n"
        r"^\s*System name:(?P<system_name>.*)\n"
        r"^\s*System Description:(?P<system_descr>.*)\s*\n"
        r"^\s*Bridge:\s+(?P<bridge>\S+)\s*\n"
        r"^\s*Router:\s+(?P<router>\S+)\s*\n"
        r"^\s*Station:\s+(?P<station>\S+)\s*\n"
        r"^\s*Wlan:\s+(?P<wlan>\S+)\s*\n",
        re.MULTILINE,
    )
    CHASSIS_TYPES = {"mac": LLDP_CHASSIS_SUBTYPE_MAC, "ifname": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME}
    PORT_TYPES = {
        "mac": LLDP_PORT_SUBTYPE_MAC,
        "ifname": LLDP_PORT_SUBTYPE_NAME,
        "local": LLDP_PORT_SUBTYPE_LOCAL,
    }

    def execute_cli(self):
        r = []
        try:  # 'Network | LLDP' always 'True'
            v = self.cli("show lldp neighbor")
        except self.CLISyntaxError:
            return []
        for match in self.rx_neighbor.finditer(v):
            local_interface = match.group("local_interface")
            i = {"local_interface": local_interface, "neighbors": []}
            v1 = self.cli("show lldp neighbors %s" % local_interface)
            for match1 in self.rx_detail.finditer(v1):
                remote_chassis_id = match1.group("chassis_id")
                remote_chassis_id_subtype = self.CHASSIS_TYPES[
                    match1.group("chassis_id_type").strip()
                ]
                remote_port = match1.group("port_id")
                remote_port_subtype = self.PORT_TYPES[match1.group("port_id_type").strip()]
                remote_capabilities = 0
                if match1.group("bridge") == "true":
                    remote_capabilities += LLDP_CAP_BRIDGE
                if match1.group("router") == "true":
                    remote_capabilities += LLDP_CAP_ROUTER
                if match1.group("station") == "true":
                    remote_capabilities += LLDP_CAP_STATION_ONLY
                if match1.group("wlan") == "true":
                    remote_capabilities += LLDP_CAP_WLAN_ACCESS_POINT
                n = {
                    "remote_chassis_id_subtype": remote_chassis_id_subtype,
                    "remote_chassis_id": remote_chassis_id,
                    "remote_port_subtype": remote_port_subtype,
                    "remote_port": remote_port,
                    "remote_capabilities": remote_capabilities,
                }
                if match1.group("port_descr") and match1.group("port_descr").strip():
                    n["remote_port_description"] = match1.group("port_descr").strip()
                if match1.group("system_name") and match1.group("system_name").strip():
                    n["remote_system_name"] = match1.group("system_name").strip()
                if match1.group("system_descr") and match1.group("system_descr").strip():
                    n["remote_system_description"] = match1.group("system_descr").strip()
                i["neighbors"].append(n)
            r.append(i)
        return r
