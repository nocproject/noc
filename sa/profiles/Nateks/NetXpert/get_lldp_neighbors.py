# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.NetXpert.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_int, is_ipv4, is_ipv6, is_mac
from noc.sa.interfaces.base import MACAddressParameter, IPv4Parameter
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
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
    name = "Nateks.NetXpert.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_summary_split = re.compile(r"^Device-ID.+?\n",
                                  re.MULTILINE | re.IGNORECASE)
    rx_s_line = re.compile(
        r"^\S+\s*(?P<local_if>(?:Fas|Gig)\S+)\s+.+$")
    rx_chassis_id = re.compile(
        r"^Chassis id:\s*(?P<id>\S+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_port = re.compile(
        "^Port id:\s*(?P<remote_if>.+?)\s*$", re.MULTILINE | re.IGNORECASE)
    rx_enabled_caps = re.compile(
        "^Enabled Capabilities:\s*(?P<caps>\S*)\s*$",
        re.MULTILINE | re.IGNORECASE)
    rx_system = re.compile(
        r"^System Name:\s*(?P<name>\S+)", re.MULTILINE | re.IGNORECASE)
    rx_descr = re.compile(r"^Port Description:\s*(?P<descr>.+)$", re.MULTILINE)

    CHASSIS_SUBTYPE = {
        "Mac Address": LLDP_CHASSIS_SUBTYPE_MAC,
        "Network Address": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
        "Local": LLDP_CHASSIS_SUBTYPE_LOCAL,
    }
    PORT_SUBTYPE = {
        "Mac Address": LLDP_PORT_SUBTYPE_MAC,
        "Interface Name": LLDP_PORT_SUBTYPE_NAME,
        "Interface Alias": LLDP_PORT_SUBTYPE_ALIAS,
        "Local": LLDP_PORT_SUBTYPE_LOCAL,
    }

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
        for line in v.splitlines():
            line = line.strip()
            if not line:
                break
            match = self.rx_s_line.match(line)
            if not match:
                continue
            lldp_interfaces += [match.group("local_if")]
        # Get LLDP neighbors
        for local_if in lldp_interfaces:
            i = {
                "local_interface": local_if,
                "neighbors": []
            }
            # Get neighbors details
            try:
                v = self.cli("show lldp neighbors interface %s" % local_if)
            except self.CLISyntaxError:
                # Found strange CLI syntax on Catalyst 4900
                # Allow ONLY interface name or "detail"
                # Need testing...
                raise self.NotSupportedError()
            # Get remote port
            match = self.re_search(self.rx_remote_port, v)
            remote_port = match.group("remote_if")
            remote_port_subtype = LLDP_PORT_SUBTYPE_ALIAS
            if is_ipv4(remote_port):
                # Actually networkAddress(4)
                remote_port = IPv4Parameter().clean(remote_port)
                remote_port_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(remote_port):
                # Actually macAddress(3)
                # Convert MAC to common form
                remote_port = MACAddressParameter().clean(remote_port)
                remote_port_subtype = LLDP_PORT_SUBTYPE_MAC
            elif is_int(remote_port):
                # Actually local(7)
                remote_port_subtype = LLDP_PORT_SUBTYPE_LOCAL
            n = {
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
                "remote_chassis_id_subtype": LLDP_CHASSIS_SUBTYPE_MAC
            }
            match = self.rx_descr.search(v)
            if match:
                n["remote_port_description"] = match.group("descr")
            # Get chassis id
            match = self.rx_chassis_id.search(v)
            if not match:
                continue
            n["remote_chassis_id"] = match.group("id")
            # Get capabilities
            cap = 0
            match = self.rx_enabled_caps.search(v)
            if match:
                for c in match.group("caps").split(","):
                    c = c.strip()
                    if c:
                        cap |= {
                            "O": LLDP_CAP_OTHER,
                            "P": LLDP_CAP_REPEATER,
                            "B": LLDP_CAP_BRIDGE,
                            "W": LLDP_CAP_WLAN_ACCESS_POINT,
                            "R": LLDP_CAP_ROUTER,
                            "T": LLDP_CAP_TELEPHONE,
                            "C": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                            "S": LLDP_CAP_STATION_ONLY,
                        }[c]
            n["remote_capabilities"] = cap
            # Get remote chassis id
            match = self.rx_system.search(v)
            if match:
                n["remote_system_name"] = match.group("name")
            if is_ipv4(n["remote_chassis_id"]) \
               or is_ipv6(n["remote_chassis_id"]):
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(n["remote_chassis_id"]):
                pass
            else:
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_LOCAL
            i["neighbors"] += [n]
            r += [i]
        return r
