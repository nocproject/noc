# ---------------------------------------------------------------------
# CData.xPON.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_ipv4, is_ipv6, is_mac
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
)


class Script(BaseScript):
    name = "CData.xPON.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_local_port = re.compile(
        r"\s*LLDP neighbor-information of (?P<port_type>xge|ge)(?P<port_num>\d+/\d+/\d+).*\n",
        re.MULTILINE,
    )
    rx_remote = re.compile(
        r"has (?P<neigh_count>\d+) neighbors\:\n"
        r".*\n"
        r"\s*Neighbor index\s+\:\s+(?P<neigh_index>\d+)\n"
        r"\s*Chassis ID type\s+\:\s+(?P<chassis_subtype>.*)\n"
        r"\s*Chassis ID\s+\:\s+(?P<chassis_id>.*)\n"
        r"(\s*Port ID type.*\n)?"
        r"(\s*Port ID\s+\:\s+(?P<port_id>.*)\n)?"
        r"\s*Port description\s+\:\s+(?P<port_descr>.*)\n"
        r"\s*System name\s+\:\s+(?P<system_name>.*)\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        with self.configure():
            v = self.cli("show lldp neighbor-info all")
            for match in self.rx_local_port.finditer(v):
                local_type = match.group("port_type")
                local_num = match.group("port_num")
                local_interface = f"{local_type}{local_num}"

                c = self.cli("show lldp neighbor-info port %s %s" % (local_type, local_num))
                for match1 in self.rx_remote.finditer(c):
                    chassis_id = match1.group("chassis_id")

                    if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                        chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
                    elif is_mac(chassis_id):
                        chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
                    else:
                        chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL

                    neighbor = {
                        "remote_chassis_id_subtype": chassis_id_subtype,
                        "remote_chassis_id": chassis_id,
                    }
                    port_descr = match1.group("port_descr").strip()
                    if port_descr:
                        neighbor["remote_port_description"] = port_descr

                    port_id = match1.group("port_id")
                    if port_id is not None:
                        if is_ipv4(port_id) or is_ipv6(port_id):
                            port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
                        elif is_mac(port_id):
                            port_id_subtype = LLDP_PORT_SUBTYPE_MAC
                        else:
                            port_id_subtype = LLDP_PORT_SUBTYPE_LOCAL

                        neighbor["remote_port_subtype"] = port_id_subtype
                        neighbor["remote_port"] = port_id
                    else:
                        neighbor["remote_port_subtype"] = LLDP_PORT_SUBTYPE_ALIAS
                        neighbor["remote_port"] = port_descr

                    r += [{"local_interface": local_interface, "neighbors": [neighbor]}]
        return r
