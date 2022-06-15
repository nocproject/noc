# ---------------------------------------------------------------------
# Symbol.AP.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter, IPv4Parameter
from noc.core.validators import is_int, is_ipv4, is_ipv6, is_mac

from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_ROUTER,
    lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "Symbol.AP.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp = re.compile(
        r"^Chassis ID: (?P<remote_id>.+)\s*\n"
        r"^System Name: (?P<remote_system_name>.+)\s*\n"
        r"^Platform: (?P<remote_system_descr>(?:.+\n)+)"
        r"^Capabilities: .+\n"
        r"^Enabled Capabilities: (?P<caps>.+)\s*\n"
        r"^Local Interface: (?P<local>ge\d+), Port ID \(outgoing port\): (?P<remote_port>.+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        c = self.cli("show lldp neighbors", cached=True)
        for n in c.split("-------------------------\n"):
            match = self.rx_lldp.search(n)
            if not match:
                continue
            remote_chassis_id = match.group("remote_id")
            if is_ipv4(remote_chassis_id) or is_ipv6(remote_chassis_id):
                remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(remote_chassis_id):
                remote_chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                n["remote_chassis_id_subtype"] = LLDP_CHASSIS_SUBTYPE_LOCAL
            remote_port = match.group("remote_port")
            remote_port_subtype = LLDP_PORT_SUBTYPE_ALIAS
            if is_ipv4(remote_port):
                remote_port = IPv4Parameter().clean(remote_port)
                remote_port_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(remote_port):
                # Convert MAC to common form
                remote_port = MACAddressParameter().clean(remote_port)
                remote_port_subtype = LLDP_PORT_SUBTYPE_MAC
            elif is_int(remote_port):
                remote_port_subtype = LLDP_PORT_SUBTYPE_LOCAL
            i = {
                "local_interface": match.group("local"),
                "neighbors": [
                    {
                        "remote_chassis_id": remote_chassis_id,
                        "remote_chassis_id_subtype": remote_chassis_id_subtype,
                        "remote_port": remote_port,
                        "remote_port_sybtype": remote_port_subtype,
                        "remote_system_name": match.group("remote_system_name"),
                        "remote_system_description": match.group("remote_system_descr").strip(),
                        "remote_capabilities": lldp_caps_to_bits(
                            match.group("caps").strip().split(" "),
                            {
                                "bridge": LLDP_CAP_BRIDGE,
                                "router": LLDP_CAP_ROUTER,
                            },
                        ),
                    }
                ],
            }
            r += [i]
        return r
