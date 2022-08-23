# ---------------------------------------------------------------------
# Cisco.NXOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.validators import is_int, is_ipv4
from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CHASSIS_SUBTYPE_MAC,
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
    name = "Cisco.NXOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_summary_split = re.compile(r"^Device ID.+?\n", re.MULTILINE | re.IGNORECASE)
    rx_s_line = re.compile(
        r"^(?:\S+\s*|\s{21})(?P<local_if>(?:Fa|Gi|Te|Eth|mgmt)\d+[\d/\.]*)\s+.+$"
    )
    rx_chassis_id = re.compile(r"^Chassis id:\s*(?P<id>\S+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_port = re.compile(r"^Port id:\s*(?P<remote_if>.+?)\s*$", re.MULTILINE | re.IGNORECASE)
    rx_enabled_caps = re.compile(
        r"^Enabled Capabilities:\s*(?P<caps>\S*)\s*$", re.MULTILINE | re.IGNORECASE
    )
    rx_system = re.compile(r"^System Name:\s*(?P<name>\S+)", re.MULTILINE | re.IGNORECASE)
    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        if v.startswith("%"):
            # % LLDP is not enabled
            return []
        v = self.rx_summary_split.split(v)[1]
        lldp_interfaces = []
        # Get LLDP interfaces with neighbors
        for ll in v.splitlines():
            ll = ll.strip()
            if not ll:
                break
            match = self.rx_s_line.match(ll)
            if not match:
                continue
            lldp_interfaces += [match.group("local_if")]
        # Get LLDP neighbors
        for local_if in lldp_interfaces:
            i = {"local_interface": local_if, "neighbors": []}
            # Get neighbors details
            try:
                v = self.cli("show lldp neighbors interface %s detail" % local_if)
            except self.CLISyntaxError:
                # Found strange CLI syntax on Catalyst 4900
                # Allow ONLY interface name or "detail"
                # Need testing...
                raise self.NotSupportedError()
            # Get remote port
            match = self.rx_remote_port.search(v)
            remote_port = match.group("remote_if")
            remote_port_subtype = LLDP_PORT_SUBTYPE_UNSPECIFIED
            if self.rx_mac.match(remote_port):
                # Convert MAC to common form
                remote_port = MACAddressParameter().clean(remote_port)
                remote_port_subtype = LLDP_PORT_SUBTYPE_MAC
            elif is_ipv4(remote_port):
                remote_port_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_int(remote_port):
                remote_port_subtype = LLDP_PORT_SUBTYPE_LOCAL
            n = {
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
                "remote_chassis_id_subtype": LLDP_CHASSIS_SUBTYPE_MAC,
            }
            # Get chassis id
            match = self.rx_chassis_id.search(v)
            if not match:
                continue
            n["remote_chassis_id"] = match.group("id")
            # Get capabilities
            cap = 0
            match = self.rx_enabled_caps.search(v)
            if match:
                cap = lldp_caps_to_bits(
                    match.group("caps").strip().split(","),
                    {
                        "o": LLDP_CAP_OTHER,
                        "p": LLDP_CAP_REPEATER,
                        "b": LLDP_CAP_BRIDGE,
                        "w": LLDP_CAP_WLAN_ACCESS_POINT,
                        "r": LLDP_CAP_ROUTER,
                        "t": LLDP_CAP_TELEPHONE,
                        "c": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                        "s": LLDP_CAP_STATION_ONLY,
                        "n/a": 0,
                    },
                )
            n["remote_capabilities"] = cap
            # Get remote chassis id
            match = self.rx_system.search(v)
            if match:
                n["remote_system_name"] = match.group("name")
            i["neighbors"] += [n]
            r += [i]
        return r
