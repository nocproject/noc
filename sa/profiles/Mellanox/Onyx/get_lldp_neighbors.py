# ---------------------------------------------------------------------
# Mellanox.Onyx.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_CHASSIS_SUBTYPE_MAC,
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
    name = "Mellanox.Onyx.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp = re.compile(
        r"^(?P<local>Eth\S+):\s*\n"
        r"^\s+Remote Index\s+: \d+\s*\n"
        r"^\s+Remote chassis id\s+: (?P<remote_id>.+)\s*\n"
        r"^\s+chassis id subtype\s+: (?P<remote_type>.+) \(\d+\)\s*\n"
        r"^\s+Remote port-id\s+: (?P<remote_port>.+)\n"
        r"^\s+port id subtype\s+: (?P<remote_port_type>.+) \(\d+\)\s*\n"
        r"^\s+Remote port description\s+: (?P<remote_port_descr>.+)\s*\n"
        r"^\s+Remote system name\s+: (?P<remote_system_name>.+)\s*\n"
        r"^\s+Remote system description\s+: (?P<remote_system_descr>(.+\n)+)\s*\n"
        r"^\s+Remote system capabilities supported: .+\n"
        r"^\s+Remote system capabilities enabled  : (?P<caps>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        c = self.cli("show lldp interfaces ethernet remote")
        for match in self.rx_lldp.finditer(c):
            i = {
                "local_interface": match.group("local"),
                "neighbors": [
                    {
                        "remote_chassis_subtype": {
                            "Mac Address": LLDP_CHASSIS_SUBTYPE_MAC,
                        }[match.group("remote_type").strip()],
                        "remote_chassis_id": match.group("remote_id"),
                        "remote_port_subtype": {
                            "Mac Address": LLDP_PORT_SUBTYPE_MAC,
                            "Interface Name": LLDP_PORT_SUBTYPE_NAME,
                        }[match.group("remote_port_type").strip()],
                        "remote_port": match.group("remote_port"),
                        "remote_port_description": match.group("remote_port_descr"),
                        "remote_system_name": match.group("remote_system_name"),
                        "remote_system_description": match.group("remote_system_descr"),
                        "remote_capabilities": lldp_caps_to_bits(
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
                            },
                        ),
                    }
                ],
            }
            r += [i]
        return r
