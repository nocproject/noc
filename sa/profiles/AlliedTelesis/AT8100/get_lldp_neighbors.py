# ---------------------------------------------------------------------
# AlliedTelesis.AT8100.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
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
    name = "AlliedTelesis.AT8100.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp = re.compile(
        r"^\s+Local (?P<local_port>port\S+):\n"
        r"^\s+Neighbors table last updated \d+ hrs \d+ mins \d+ secs ago\n"
        r"^\s+Chassis ID Type \.+ (?P<chassis_id_subtype>.+?)\n"
        r"^\s+Chassis ID \.+ (?P<chassis_id>.+?)\n"
        r"^\s+Port ID Type \.+ (?P<port_id_subtype>.+?)\n"
        r"^\s+Port ID \.+ (?P<port_id>.+?)\n"
        r"^\s+TTL \.+ \d+ \(secs\)\n"
        r"^\s+Port Description \.+ (?P<port_description>.+?)\n"
        r"^\s+System Name \.+ (?P<system_name>.+?)\n"
        r"^\s+System Description \.+ (?P<system_description>.+?)\n"
        r"^\s+System Capabilities - Supported \.+ (?P<caps>.+?)\n",
        re.MULTILINE | re.DOTALL,
    )

    CHASSIS_SUBTYPE = {
        "MAC address": LLDP_CHASSIS_SUBTYPE_MAC,
    }
    PORT_SUBTYPE = {
        "Interface alias": LLDP_PORT_SUBTYPE_ALIAS,
        "MAC address": LLDP_PORT_SUBTYPE_MAC,
        "Interface name": LLDP_PORT_SUBTYPE_NAME,
    }

    def execute_cli(self):
        r = []
        v = self.cli("show lldp neighbors detail")
        for match in self.rx_lldp.finditer(v):
            iface = {"local_interface": match.group("local_port"), "neighbors": []}
            if match.group("caps").strip() != "[not advertised]":
                cap = lldp_caps_to_bits(
                    match.group("caps").strip().split(", "),
                    {
                        "other": LLDP_CAP_OTHER,
                        "repeater": LLDP_CAP_REPEATER,
                        "bridge": LLDP_CAP_BRIDGE,
                        "access point": LLDP_CAP_WLAN_ACCESS_POINT,
                        "router": LLDP_CAP_ROUTER,
                        "telephone": LLDP_CAP_TELEPHONE,
                        "d": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                        "station only": LLDP_CAP_STATION_ONLY,
                    },
                )
            else:
                cap = 0
            n = {
                "remote_chassis_id": match.group("chassis_id").strip(),
                "remote_chassis_id_subtype": self.CHASSIS_SUBTYPE[
                    match.group("chassis_id_subtype").strip()
                ],
                "remote_port": match.group("port_id").strip(),
                "remote_port_subtype": self.PORT_SUBTYPE[match.group("port_id_subtype").strip()],
                "remote_capabilities": cap,
            }
            system_name = match.group("system_name").strip()
            if system_name and system_name != "[not advertised]":
                n["remote_system_name"] = system_name
            system_description = match.group("system_description").strip()
            if system_description and system_description != "[not advertised]":
                n["remote_system_description"] = re.sub(r"\s+", " ", system_description)
            port_description = match.group("port_description").strip()
            if port_description and port_description != "[not advertised]":
                n["remote_port_description"] = re.sub(r"\s+", " ", port_description)
            iface["neighbors"] += [n]
            r += [iface]
        return r
