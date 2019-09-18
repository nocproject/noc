# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.ALS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.validators import is_ipv4, is_ipv6
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
    name = "Alstec.ALS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    blank_line = re.compile(r"^\s{79}\n", re.MULTILINE)

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
            # This is strange behavior, but it helps us
            v = self.blank_line.sub("", v)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        t = parse_table(v, allow_wrap=True, allow_extend=True)
        for i in t:
            chassis_id = i[1]
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            else:
                try:
                    MACAddressParameter().clean(chassis_id)
                    chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
                except ValueError:
                    chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
            port_id = i[2]
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            else:
                try:
                    MACAddressParameter().clean(port_id)
                    port_id_subtype = LLDP_PORT_SUBTYPE_MAC
                except ValueError:
                    port_id_subtype = LLDP_PORT_SUBTYPE_LOCAL
            caps = lldp_caps_to_bits(
                i[4].split(","),
                {
                    "o": LLDP_CAP_OTHER,
                    "p": LLDP_CAP_REPEATER,
                    "b": LLDP_CAP_BRIDGE,
                    "w": LLDP_CAP_WLAN_ACCESS_POINT,
                    "r": LLDP_CAP_ROUTER,
                    "t": LLDP_CAP_TELEPHONE,
                    "c": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                    "s": LLDP_CAP_STATION_ONLY,
                },
            )
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps,
            }
            if i[3]:
                neighbor["remote_system_name"] = i[3]
            r += [{"local_interface": i[0], "neighbors": [neighbor]}]
        return r
