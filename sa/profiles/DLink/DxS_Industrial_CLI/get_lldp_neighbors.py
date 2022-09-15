# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.sa.interfaces.base import IPv4Parameter
from noc.core.text import parse_table
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
    name = "DLink.DxS_Industrial_CLI.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_entity = re.compile(
        r"^\s+Chassis ID Subtype\s+:(?P<chassis_id_type>.+)\s*\n"
        r"^\s+Chassis ID\s+:(?P<chassis_id>.+)\s*\n"
        r"^\s+Port ID Subtype\s+:(?P<port_id_type>.+)\s*\n"
        r"^\s+Port ID\s+:(?P<port_id>.+)\s*\n"
        r"^\s+Port Description\s+:(?P<port_description>(.|\n)*)\n"
        r"^\s+System Name\s+:(?P<system_name>(.|\n)*)\n"
        r"^\s+System Description\s+:(?P<system_description>(.|\n)*)\n"
        r"^\s+System Capabilities\s+:(?P<system_capabilities>.*)\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        has_if_range = False
        v = self.cli("show interfaces status")
        t = parse_table(v)
        for i in t:
            # Convert eth1/0/21(f) to eth1/0/21 ans skip eth1/0/21(c)
            ifname = i[0].replace("(f)", "")
            if "(c)" in ifname:
                continue
            iface = {"local_interface": ifname, "neighbors": []}
            if_range = "%s-%s" % (ifname[3:], ifname.split("/")[2])
            if not has_if_range:
                try:
                    v = self.cli("show lldp neighbors interface %s" % ifname)
                except self.CLISyntaxError:
                    v = self.cli("show lldp neighbors interface ethernet %s" % if_range)
                    has_if_range = True
            else:
                v = self.cli("show lldp neighbors interface ethernet %s" % if_range)
            for m in self.rx_entity.finditer(v):
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
                    "local": LLDP_PORT_SUBTYPE_LOCAL,
                }[remote_port_subtype.strip().lower()]
                n["remote_port"] = m.group("port_id").strip()
                if n["remote_port_subtype"] == 3:
                    n["remote_port"] = MACAddressParameter().clean(n["remote_port"])
                if n["remote_port_subtype"] == 4:
                    n["remote_port"] = IPv4Parameter().clean(n["remote_port"])

                if m.group("port_description").strip():
                    n["remote_port_description"] = re.sub(
                        r"\n\s*", "", m.group("port_description").strip()
                    )
                if m.group("system_name").strip():
                    n["remote_system_name"] = re.sub(
                        r"\n\s*", "", m.group("system_name").strip()
                    )
                if m.group("system_description").strip():
                    n["remote_system_description"] = re.sub(
                        r"\n\s*", "", m.group("system_description").strip()
                    )
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
                iface["neighbors"] += [n]
            if iface["neighbors"]:
                r += [iface]
        return r
