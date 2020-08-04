# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modiles
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
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_AGENT_CIRCUIT_ID,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_OTHER,
    LLDP_CAP_REPEATER,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_WLAN_ACCESS_POINT,
    LLDP_CAP_ROUTER,
    LLDP_CAP_TELEPHONE,
    LLDP_CAP_DOCSIS_CABLE_DEVICE,
    LLDP_CAP_STATION_ONLY,
    lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_port = re.compile(
        r"^-+\s*\n"
        r"^Lldp neighbor-information of port \[(?P<port>.+?)\]\s*\n"
        r"^-+\s*\n"
        r"(?P<entities>.+?)\n"
        r"^\s+Maximum frame Size\s+:(\s+\d+)?\s*",
        re.MULTILINE | re.DOTALL,
    )
    rx_entity = re.compile(
        r"^\s+Chassis ID type\s+:(?P<chassis_id_type>.+)\s*\n"
        r"^\s+Chassis ID\s+:(?P<chassis_id>.+)\s*\n"
        r"^\s+System name\s+:(?P<system_name>.*)\n"
        r"^\s+System description\s+:(?P<system_description>(.|\n)*)\n"
        r"^\s+System capabilities supported\s+:(?P<system_capabilities>.*)\s*\n"
        r"^\s+System capabilities enabled\s+:(?P<system_capabilities_>.*)\s*\n"
        r"(^\s*\n)?"
        r"(^\s+Management address subtype\s+:(?P<mgmt_addr_type>.+)\s*\n)?"
        r"(^\s+Management address\s+:(?P<mgmt_addr>.+)\s*\n)?"
        r"(^\s+Interface numbering subtype\s+:(?P<interface_numbering_subtype>.+)\s*\n)?"
        r"(^\s+Interface number\s+:(?P<interface_number>.+)\s*\n)?"
        r"(^\s+Object identifier\s+:.*\n)?"
        r"(^\s*\n)?"
        r"(^\s*\n)?"
        r"^\s+Port ID type\s+:(?P<port_id_type>.+)\s*\n"
        r"^\s+Port ID\s+:(?P<port_id>.+)\s*\n"
        r"^\s+Port description\s+:(?P<port_description>.*)\n",
        re.MULTILINE,
    )

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp neighbor-information")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_port.finditer(v):
            i = {"local_interface": match.group("port"), "neighbors": []}
            for m in self.rx_entity.finditer(match.group("entities")):
                n = {}
                n["remote_chassis_id_subtype"] = {
                    "chassis component": LLDP_CHASSIS_SUBTYPE_CHASSIS_COMPONENT,
                    "interface alias": LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
                    "port component": LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
                    "mac address": LLDP_CHASSIS_SUBTYPE_MAC,
                    "network address": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
                    "interface name": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
                    "local": LLDP_CHASSIS_SUBTYPE_LOCAL,
                }[m.group("chassis_id_type").strip().lower()]
                n["remote_chassis_id"] = m.group("chassis_id").strip()
                remote_port_subtype = m.group("port_id_type")
                remote_port_subtype.replace("_", " ")
                n["remote_port_subtype"] = {
                    "interface alias": LLDP_PORT_SUBTYPE_ALIAS,
                    "port component": LLDP_PORT_SUBTYPE_COMPONENT,
                    "mac address": LLDP_PORT_SUBTYPE_MAC,
                    "network address": LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
                    "interface name": LLDP_PORT_SUBTYPE_NAME,
                    "agent circuit id": LLDP_PORT_SUBTYPE_AGENT_CIRCUIT_ID,
                    "locally assigned": LLDP_PORT_SUBTYPE_LOCAL,
                }[remote_port_subtype.strip().lower()]
                n["remote_port"] = m.group("port_id").strip()
                if m.group("port_description").strip():
                    n["remote_port_description"] = m.group("port_description").strip()
                if m.group("system_name").strip():
                    n["remote_system_name"] = m.group("system_name").strip()
                if m.group("system_description").strip():
                    n["remote_system_description"] = m.group("system_description").strip()
                if m.group("system_capabilities"):
                    caps = lldp_caps_to_bits(
                        m.group("system_capabilities").split(","),
                        {
                            "other": LLDP_CAP_OTHER,
                            "repeater": LLDP_CAP_REPEATER,
                            "bridge": LLDP_CAP_BRIDGE,
                            "wlan access point": LLDP_CAP_WLAN_ACCESS_POINT,
                            "router": LLDP_CAP_ROUTER,
                            "telephone": LLDP_CAP_TELEPHONE,
                            "docsis cable device": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                            "station only": LLDP_CAP_STATION_ONLY,
                        },
                    )
                    n["remote_capabilities"] = caps
                i["neighbors"] += [n]
            if i["neighbors"]:
                r += [i]
        return r
