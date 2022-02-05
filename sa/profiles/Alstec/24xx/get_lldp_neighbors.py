# ---------------------------------------------------------------------
# Alstec.24xx.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.core.text import parse_table
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.validators import is_ipv4, is_ipv6
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
)


class Script(BaseScript):
    name = "Alstec.24xx.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    always_prefer = "S"

    rx_line = re.compile(
        r"^(?P<port>(?:Gi|Te|Po|e|g|cch)\S+)\s+(?P<system_id>\S+)\s+"
        r"(?P<port_id>\S+)\s+(?P<system_name>.*)\s+(?P<caps>\S+)\s+\d+",
        re.IGNORECASE,
    )

    CAPS = {
        "": 0,
        "O": LLDP_CAP_OTHER,
        "r": LLDP_CAP_REPEATER,
        "B": LLDP_CAP_BRIDGE,
        "W": LLDP_CAP_WLAN_ACCESS_POINT,
        "R": LLDP_CAP_ROUTER,
        "T": LLDP_CAP_TELEPHONE,
        "D": LLDP_CAP_DOCSIS_CABLE_DEVICE,
        "H": LLDP_CAP_STATION_ONLY,
    }

    def execute_cli(self, **kwargs):
        r = []
        data = []
        try:
            v = self.cli("show lldp remote-device all")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        v = v.replace("\n\n", "\n")
        for ll in parse_table(v, allow_extend=True):
            if not ll[0]:
                data[-1] = [s[0] + s[1] for s in zip(data[-1], ll)]
                continue
            data += [ll]
        for d in data:
            chassis_id = d[2]
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            else:
                try:
                    MACAddressParameter().clean(chassis_id)
                    chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
                except ValueError:
                    chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
            port_id = d[3]
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            else:
                try:
                    MACAddressParameter().clean(port_id)
                    port_id_subtype = LLDP_PORT_SUBTYPE_MAC
                except ValueError:
                    port_id_subtype = LLDP_PORT_SUBTYPE_LOCAL
            # caps = sum([self.CAPS[s.strip()] for s in d[4].split(",")])
            caps = 0
            if not chassis_id:
                continue
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps,
            }
            """
                if match.group("system_name"):
                    neighbor["remote_system_name"] = match.group("system_name")
                """
            neighbor["remote_system_name"] = d[4]
            r += [
                {
                    # "local_interface": match.group("port"),
                    "local_interface": d[0],
                    "neighbors": [neighbor],
                }
            ]
        return r
