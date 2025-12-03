# ---------------------------------------------------------------------
# OS.FreeBSD.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_UNSPECIFIED,
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
    name = "OS.FreeBSD.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_entry = re.compile(r"^\-+(?P<item>.+?)TTL:\s+\d+\n", re.MULTILINE | re.DOTALL)

    rx_item = re.compile(
        r"^Interface:\s+(?P<local_interface>\S+), via: LLDP.+\n"
        r"^\s+Chassis:\s+\n"
        r"^\s+ChassisID:\s+(?P<remote_chassis_id_subtype>\S+)\s+(?P<remote_chassis_id>\S+)\n"
        r"(^\s+SysName:\s+(?P<remote_system_name>\S+)\n)?"
        r"(^\s+SysDescr:\s+(?P<remote_system_description>.+)\n)?"
        r"^\s+MgmtIP:\s+\S+\n"
        r"^\s+Capability:\s+(?P<capabilities>.+)\n"
        r"^\s+Port:\s+\n"
        r"^\s+PortID:\s+(?P<remote_port_subtype>\S+)\s+(?P<remote_port>\S+)\n"
        r"(^\s+PortDescr:\s+(?P<remote_port_description>\S+)\n)?",
        re.MULTILINE | re.DOTALL,
    )
    rx_item_no_mgmt = re.compile(
        r"^Interface:\s+(?P<local_interface>\S+), via: LLDP.+\n"
        r"^\s+Chassis:\s+\n"
        r"^\s+ChassisID:\s+(?P<remote_chassis_id_subtype>\S+)\s+(?P<remote_chassis_id>\S+)\n"
        r"(^\s+SysName:\s+(?P<remote_system_name>\S+)\n)?"
        r"(^\s+SysDescr:\s+(?P<remote_system_description>.+)\n)?"
        r"^\s+Capability:\s+(?P<capabilities>.+)\n"
        r"^\s+Port:\s+\n"
        r"^\s+PortID:\s+(?P<remote_port_subtype>\S+)\s+(?P<remote_port>\S+)\n"
        r"(^\s+PortDescr:\s+(?P<remote_port_description>\S+)\n)?",
        re.MULTILINE | re.DOTALL,
    )
    rx_line = re.compile(r"^(?P<tlv>\S+)\_\d+\=\'(?P<value>\S*)\'", re.MULTILINE)

    def execute_cli(self):
        neighbors = []

        # Try lldpd first
        try:
            v = self.cli("lldpcli show neighbors")
        except self.CLISyntaxError:
            pass
        for match in self.rx_entry.finditer(v):
            entry = match.group("item")
            match1 = self.rx_item.search(entry)
            if not match1:
                match1 = self.rx_item_no_mgmt.search(entry)
                if not match1:
                    continue
            n = {
                "remote_chassis_id": match1.group("remote_chassis_id"),
                "remote_port": match1.group("remote_port"),
            }
            n["remote_chassis_id_subtype"] = {
                "ifalias": LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
                "mac": LLDP_CHASSIS_SUBTYPE_MAC,
                "ip": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
                "ifname": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
                "local": LLDP_CHASSIS_SUBTYPE_LOCAL,
                "unhandled": LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
            }[match1.group("remote_chassis_id_subtype")]
            n["remote_port_subtype"] = {
                "ifalias": LLDP_PORT_SUBTYPE_ALIAS,
                "mac": LLDP_PORT_SUBTYPE_MAC,
                "ip": LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
                "ifname": LLDP_PORT_SUBTYPE_NAME,
                "local": LLDP_PORT_SUBTYPE_LOCAL,
                "unhandled": LLDP_PORT_SUBTYPE_UNSPECIFIED,
            }[match1.group("remote_port_subtype")]
            if match1.group("remote_system_name") and match1.group("remote_system_name").strip():
                n["remote_system_name"] = match1.group("remote_system_name")
            if (
                match1.group("remote_system_description")
                and match1.group("remote_system_description").strip()
            ):
                n["remote_system_description"] = match1.group("remote_system_description")
                n["remote_system_description"] = re.sub(
                    r"\n\s{18}", "", n["remote_system_description"]
                )
            if (
                match1.group("remote_port_description")
                and match1.group("remote_port_description").strip()
            ):
                n["remote_port_description"] = match1.group("remote_port_description")
            caps = match1.group("capabilities")
            cap = 0
            if "Other, on" in caps:
                cap |= LLDP_CAP_OTHER
            if "Repeater, on" in caps:
                cap |= LLDP_CAP_REPEATER
            if "Bridge, on" in caps:
                cap |= LLDP_CAP_BRIDGE
            if "Wlan, on" in caps:
                cap |= LLDP_CAP_WLAN_ACCESS_POINT
            if "Router, on" in caps:
                cap |= LLDP_CAP_ROUTER
            if "Tel, on" in caps:
                cap |= LLDP_CAP_TELEPHONE
            if "Docsis, on" in caps:
                cap |= LLDP_CAP_DOCSIS_CABLE_DEVICE
            if "Station, on" in caps:
                cap |= LLDP_CAP_STATION_ONLY
            n["remote_capabilities"] = cap
            neighbors.append({"local_interface": match1.group("local_interface"), "neighbors": [n]})

        if neighbors:
            return neighbors

        # Last resort
        try:
            v = self.cli("ladvdc -b -L")
        except self.CLISyntaxError:
            pass

        for match in self.rx_line.finditer(v):
            tlv = match.group(1)
            value = match.group(2)
            if tlv == "INTERFACE":
                local_interface = value
                n = {}
            elif tlv == "HOSTNAME":
                n["remote_chassis_id"] = value
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_LOCAL
            elif tlv == "ADDR_INET4":
                n["remote_chassis_id"] = value
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif tlv == "PORTNAME":
                n["remote_port"] = value
                n["remote_port_subtype"] = LLDP_PORT_SUBTYPE_NAME
            elif tlv == "PORTDESCR":
                n["remote_port_description"] = value
            elif tlv == "CAPABILITIES":
                value = value.replace("r", "repeater")
                cap = lldp_caps_to_bits(
                    value.split(),
                    {
                        "o": LLDP_CAP_OTHER,
                        "repeater": LLDP_CAP_REPEATER,
                        "b": LLDP_CAP_BRIDGE,
                        "w": LLDP_CAP_WLAN_ACCESS_POINT,
                        "r": LLDP_CAP_ROUTER,
                        "t": LLDP_CAP_TELEPHONE,
                        "c": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                        "s": LLDP_CAP_STATION_ONLY,
                    },
                )
                n["remote_capabilities"] = cap
            elif tlv == "HOLDTIME":  # last TLV
                if n["remote_chassis_id"] != "":
                    neighbors.append({"local_interface": local_interface, "neighbors": [n]})
        return neighbors
