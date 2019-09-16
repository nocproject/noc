# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_ipv4, is_ipv6, is_mac
from noc.core.text import parse_table
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
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


class Script(BaseScript):
    name = "Eltex.MA4000.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_neighbor = re.compile(
        r"^Device ID: (?P<chassis_id>\S+)\s*\n"
        r"^Port ID: (?:\S+ )?(?:\| )?(?P<port_id>\S+)\s*\n"
        r"^Time To Live: \S+\s*\n\n"
        r"(^Port description:(?P<port_descr>.*)\n)?"
        r"(^System name:(?P<system_name>.*)\n)?"
        r"(^System description:(?P<system_descr>.*)\n)?",
        re.MULTILINE,
    )
    rx_caps = re.compile(r"^Capabilities:(?P<caps>.+)\n\n", re.MULTILINE)

    def execute_cli(self):
        r = []
        t = parse_table(self.cli("show lldp neighbor"), allow_wrap=True)
        for i in t:
            c = self.cli("show lldp neighbor %s" % i[0])
            match = self.rx_neighbor.search(c)
            chassis_id = match.group("chassis_id")
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
            port_id = match.group("port_id")
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_MAC
            else:
                port_id_subtype = LLDP_PORT_SUBTYPE_LOCAL
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
            }
            if match.group("port_descr"):
                port_descr = match.group("port_descr").strip()
                if port_descr:
                    neighbor["remote_port_description"] = port_descr
            if match.group("system_name"):
                system_name = match.group("system_name").strip()
                if system_name:
                    neighbor["remote_system_name"] = system_name
            if match.group("system_descr"):
                system_descr = match.group("system_descr").strip()
                if system_descr:
                    neighbor["remote_system_description"] = system_descr
            caps = 0
            match = self.rx_caps.search(c)
            if match:
                caps = lldp_caps_to_bits(
                    match.group("caps").strip().split(","),
                    {
                        "other": LLDP_CAP_OTHER,
                        "repeater": LLDP_CAP_REPEATER,
                        "bridge": LLDP_CAP_BRIDGE,
                        "access point": LLDP_CAP_WLAN_ACCESS_POINT,
                        "router": LLDP_CAP_ROUTER,
                        "telephone": LLDP_CAP_TELEPHONE,
                        "cable device": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                        "station only": LLDP_CAP_STATION_ONLY,
                    },
                )
            neighbor["remote_capabilities"] = caps

            r += [{"local_interface": i[0], "neighbors": [neighbor]}]
        return r
