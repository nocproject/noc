# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_lldp_neighbors
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
    LLDP_CHASSIS_SUBTYPE_CHASSIS_COMPONENT,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
    LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_REPEATER,
    LLDP_CAP_ROUTER,
    lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_int = re.compile(r"Table on\s*(?P<interface>\S+)")
    rx_ChassisID = re.compile(
        r"ChassisID:\s+\|\s*(?P<chassis_id>\S+)\s\((?P<chassis_sub>[a-z\s]*)\)"
    )
    rx_PortID = re.compile(r"PortID:\s+\|\s*(?P<port_id>\S+)\s\((?P<port_subtype>[a-zN\s]*)\)")
    rx_PortDescr = re.compile(r"PortDescr:\s+\|\s*(?P<port_descr>.+?)\|")
    rx_Caps = re.compile(r"Caps:\s+\|\s*(?P<caps>[^\n]*)\|")

    def execute_cli(self, **kwargs):
        result = []
        lldp = self.cli("lldp report")
        for match in self.rx_int.finditer(lldp):
            if "ChassisID" not in lldp:
                continue
            result += [
                {
                    "local_interface": match.group("interface"),
                    "neighbors": [
                        {
                            "remote_chassis_id_subtype": {
                                "chassis component": LLDP_CHASSIS_SUBTYPE_CHASSIS_COMPONENT,
                                "interface alias": LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
                                "port component": LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
                                "mac": LLDP_CHASSIS_SUBTYPE_MAC,
                                "network address": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
                                "interface name": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
                                "local": LLDP_CHASSIS_SUBTYPE_LOCAL,
                            }[self.rx_ChassisID.search(lldp).group("chassis_sub").lower()],
                            "remote_chassis_id": self.rx_ChassisID.search(lldp).group("chassis_id"),
                            "remote_port_subtype": {
                                "interface alias": LLDP_PORT_SUBTYPE_ALIAS,
                                "port component": LLDP_PORT_SUBTYPE_COMPONENT,
                                "mac": LLDP_PORT_SUBTYPE_MAC,
                                "ifname": LLDP_PORT_SUBTYPE_NAME,
                                "local": LLDP_PORT_SUBTYPE_LOCAL,
                            }[self.rx_PortID.search(lldp).group("port_subtype").lower()],
                            "remote_port": self.rx_PortID.search(lldp).group("port_id"),
                            "remote_port_description": self.rx_PortDescr.search(lldp)
                            .group("port_descr")
                            .strip(),
                            "remote_capabilities": lldp_caps_to_bits(
                                self.rx_Caps.search(lldp).group("caps").strip().lower().split(", "),
                                {
                                    "repeater*": LLDP_CAP_REPEATER,
                                    "bridge*": LLDP_CAP_BRIDGE,
                                    "router*": LLDP_CAP_ROUTER,
                                },
                            ),
                        }
                    ],
                }
            ]
        return result
