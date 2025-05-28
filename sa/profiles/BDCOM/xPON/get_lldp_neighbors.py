# ---------------------------------------------------------------------
# BDCOM.xPON.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
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
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
)


class Script(BaseScript):
    name = "BDCOM.xPON.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_local_port = re.compile(r"^\S*\s+(?P<port>(Gig|TGi)\d+\S+)\s+", re.MULTILINE)
    rx_remote1 = re.compile(
        r"^chassis id: (?P<chassis_id>\S+)\s*\n"
        r"^port id: (?P<port_id>.+)\s*\n"
        r"^port description: (?P<port_descr>(.*\n)+)"
        r"^system name: (?P<system_name>.*)\s*\n",
        re.MULTILINE,
    )
    rx_remote2 = re.compile(
        r"^chassis id: (?P<chassis_id>\S+)\s*\n"
        r"^chassis id subtype: (?P<chassis_id_subtype>.+?)\s*\n"
        r"^port id: (?P<port_id>.+)\s*\n"
        r"^port id subtype: (?P<port_id_subtype>.+?)\s*\n"
        r"^port description: (?P<port_descr>(.*\n)+)"
        r"^system name: (?P<system_name>.*)\s*\n",
        re.MULTILINE,
    )
    rx_sys_descr = re.compile(r"^system description: (?P<sys_descr>.+)\s*\n", re.MULTILINE)

    def execute_cli(self):
        r = []
        v = self.cli("show lldp neighbors")
        for match in self.rx_local_port.finditer(v):
            local_interface = match.group("port")
            c = self.cli("show lldp neighbors interface %s" % local_interface)
            match1 = self.rx_remote1.search(c)
            if match1:
                chassis_id = match1.group("chassis_id")
                if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                    chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
                elif is_mac(chassis_id):
                    chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
                else:
                    chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
                port_id = match1.group("port_id")
                if is_ipv4(port_id) or is_ipv6(port_id):
                    port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
                elif is_mac(port_id):
                    port_id_subtype = LLDP_PORT_SUBTYPE_MAC
                else:
                    port_id_subtype = LLDP_PORT_SUBTYPE_LOCAL
            else:
                match1 = self.rx_remote2.search(c)
                chassis_id = match1.group("chassis_id")
                chassis_id_subtype = {
                    "mac address": LLDP_CHASSIS_SUBTYPE_MAC,
                    "network address": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
                    "locally assigned": LLDP_CHASSIS_SUBTYPE_LOCAL,
                }[match1.group("chassis_id_subtype").strip().lower()]

                port_id = match1.group("port_id")
                port_id_subtype = {
                    "port component": LLDP_PORT_SUBTYPE_COMPONENT,
                    "mac address": LLDP_PORT_SUBTYPE_MAC,
                    "network address": LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
                    "interface name": LLDP_PORT_SUBTYPE_NAME,
                    "locally assigned": LLDP_PORT_SUBTYPE_LOCAL,
                }[match1.group("port_id_subtype").strip().lower()]
            port_descr = match1.group("port_descr").strip()
            neighbor = {
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_chassis_id": chassis_id,
                "remote_port_subtype": port_id_subtype,
                "remote_port": port_id,
                "remote_system_name": match1.group("system_name"),
            }
            match1 = self.rx_sys_descr.search(c)
            if match1:
                neighbor["remote_system_description"] = match1.group("sys_descr")
            if port_descr and "-- not advertised" not in port_descr:
                neighbor["remote_port_description"] = port_descr
            found = False
            for i in r:
                if i["local_interface"] == local_interface:
                    i["neighbors"] += [neighbor]
                    found = True
                    break
            if not found:
                r += [{"local_interface": local_interface, "neighbors": [neighbor]}]
        return r
