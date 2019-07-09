# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXA10.get_lldp_neighbors
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
)


class Script(BaseScript):
    name = "ZTE.ZXA10.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_neighbor = re.compile(r"^(?P<local_interface>gei_\d+/\d+/\d+)\s+", re.MULTILINE)
    rx_detail = re.compile(
        r"^Chassis ID: (?P<chassis_id>\S+) \| (?P<chassis_id_type>.+)\n"
        r"^Peer Port: (?P<port_id>\S+) \| (?P<port_id_type>.+)\n"
        r"^.+\n"
        r"(^System Name: (?P<system_name>.+)\n)?"
        r"(^System Description: (?P<system_descr>.+)\n)?",
        re.MULTILINE,
    )
    CHASSIS_TYPES = {
        "MAC Address": LLDP_CHASSIS_SUBTYPE_MAC,
        "Interface Name": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    }
    PORT_TYPES = {"MAC Address": LLDP_PORT_SUBTYPE_MAC, "Interface Name": LLDP_PORT_SUBTYPE_NAME}

    def execute_cli(self):
        r = []
        v = self.cli("show lldp neighbor")
        for match in self.rx_neighbor.finditer(v):
            local_interface = match.group("local_interface")
            v1 = self.cli("show lldp entry interface %s" % local_interface)
            match1 = self.rx_detail.search(v1)
            remote_chassis_id = match1.group("chassis_id")
            remote_chassis_id_subtype = self.CHASSIS_TYPES[match1.group("chassis_id_type").strip()]
            remote_port = match1.group("port_id")
            remote_port_subtype = self.PORT_TYPES[match1.group("port_id_type").strip()]
            remote_capabilities = 0
            i = {"local_interface": local_interface, "neighbors": []}
            n = {
                "remote_chassis_id_subtype": remote_chassis_id_subtype,
                "remote_chassis_id": remote_chassis_id,
                "remote_port_subtype": remote_port_subtype,
                "remote_port": remote_port,
                "remote_capabilities": remote_capabilities,
            }
            if match1.group("system_name") and match1.group("system_name").strip():
                n["remote_system_name"] = match1.group("system_name").strip()
            if match1.group("system_descr") and match1.group("system_descr").strip():
                n["remote_system_description"] = match1.group("system_descr").strip()
            i["neighbors"].append(n)
            r.append(i)
        return r
