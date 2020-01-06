# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.validators import is_int, is_ipv4, is_ipv6, is_mac
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
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
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_detail = re.compile(
        r"^Device ID: (?P<dev_id>\S+)\s*\n"
        r"^Port ID: (?P<port_id>\S+)\s*\n"
        r"^Capabilities:(?P<caps>.*)\n"
        r"^System Name:(?P<sys_name>.*)\n"
        r"^System description:(?P<sys_descr>(?:.*\n)*?)"
        r"^Port description:(?P<port_descr>.*)\n",
        re.MULTILINE,
    )

    rx_header_start = re.compile(r"^\s*[-=]+[\s\+]+[-=]+")
    rx_col = re.compile(r"^([\s\+]*)([\-]+|[=]+)")

    def execute_cli(self):
        r = []
        # Fallback to CLI
        lldp = self.cli("show lldp neighbors")
        for link in parse_table(
            lldp, allow_wrap=True, line_wrapper=None, row_wrapper=lambda x: x.strip()
        ):
            local_interface = link[0]
            remote_chassis_id = link[1]
            remote_port = link[2]
            remote_system_name = link[3]
            # Build neighbor data
            # Get capability
            cap = lldp_caps_to_bits(
                link[4].strip().split(","),
                {
                    "O": LLDP_CAP_OTHER,
                    "r": LLDP_CAP_REPEATER,
                    "B": LLDP_CAP_BRIDGE,
                    "W": LLDP_CAP_WLAN_ACCESS_POINT,
                    "R": LLDP_CAP_ROUTER,
                    "T": LLDP_CAP_TELEPHONE,
                    "D": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                    "S": LLDP_CAP_STATION_ONLY,  # S-VLAN
                    "C": 256,  # C-VLAN
                    "H": 512,  # Host
                    "TP": 1024,  # Two Ports MAC Relay
                },
            )
            if is_ipv4(remote_chassis_id) or is_ipv6(remote_chassis_id):
                remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(remote_chassis_id):
                remote_chassis_id = MACAddressParameter().clean(remote_chassis_id)
                remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
            # Get remote port subtype
            remote_port_subtype = LLDP_PORT_SUBTYPE_ALIAS
            if is_ipv4(remote_port):
                # Actually networkAddress(4)
                remote_port_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(remote_port):
                # Actually macAddress(3)
                # Convert MAC to common form
                remote_port = MACAddressParameter().clean(remote_port)
                remote_port_subtype = LLDP_PORT_SUBTYPE_MAC
            elif is_int(remote_port):
                # Actually local(7)
                remote_port_subtype = LLDP_PORT_SUBTYPE_LOCAL
            i = {"local_interface": local_interface, "neighbors": []}
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_chassis_id_subtype": remote_chassis_id_subtype,
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
                "remote_capabilities": cap,
            }
            if remote_system_name:
                n["remote_system_name"] = remote_system_name
            #
            # XXX: Dirty hack for older firmware. Switch rebooted.
            #
            if remote_chassis_id_subtype != LLDP_CHASSIS_SUBTYPE_LOCAL:
                i["neighbors"] = [n]
                r += [i]
                continue
            try:
                c = self.cli("show lldp neighbors %s" % local_interface)
                match = self.rx_detail.search(c)
                if match:
                    remote_chassis_id = match.group("dev_id")
                    if is_ipv4(remote_chassis_id) or is_ipv6(remote_chassis_id):
                        remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
                    elif is_mac(remote_chassis_id):
                        remote_chassis_id = MACAddressParameter().clean(remote_chassis_id)
                        remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
                    else:
                        remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
                    n["remote_chassis_id"] = remote_chassis_id
                    n["remote_chassis_id_subtype"] = remote_chassis_id_subtype
                    if match.group("sys_name").strip():
                        sys_name = match.group("sys_name").strip()
                        n["remote_system_name"] = sys_name
                    if match.group("sys_descr").strip():
                        sys_descr = match.group("sys_descr").strip()
                        n["remote_system_description"] = sys_descr
                    if match.group("port_descr").strip():
                        port_descr = match.group("port_descr").strip()
                        n["remote_port_description"] = port_descr
            except Exception:
                pass
            i["neighbors"] += [n]
            r += [i]
        return r
