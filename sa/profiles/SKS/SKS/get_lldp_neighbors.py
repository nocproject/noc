# ---------------------------------------------------------------------
# SKS.SKS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
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
    name = "SKS.SKS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_neighbor = re.compile(
        r"^chassis id: (?P<chassis_id>\S+)\s*\n"
        r"^port id: (?P<port_id>\S+)\s*\n"
        r"^port description:(?P<port_descr>.*)\n"
        r"^system name:(?P<system_name>.*)\n"
        r"^system description:(?P<system_descr>(.*\n)*?)"
        r"^Time remaining: \d+\s*\n"
        r"^system capabilities:.*\n"
        r"^enabled capabilities:(?P<caps>.*?)\n",
        re.MULTILINE,
    )

    rx_neighbor_table = re.compile(
        r"^(\S+|\S+\n\S+)\s+(?P<local_iface>(?:Gig|TGi)\d\/\d+)\s+", re.MULTILINE
    )

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        t = parse_table(v, allow_wrap=True)
        for i in t:
            chassis_id = i[1]
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
            port_id = i[2]
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_MAC
            else:
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
        if not t:
            # Fix for SKS-16E1-IP-ES-L, Reduce 'show lldp neighbors interface XXX' command
            # because multiple run causes stuck cli on device.
            match = self.rx_neighbor_table.findall(v)
            if match:
                ifaces = [x[1] for x in match]
            else:
                ifaces = [x["interface"] for x in self.scripts.get_interface_status()]
            for iface in ifaces:
                c = self.cli(f"show lldp neighbors interface {iface}", ignore_errors=True)
                c = c.replace("\n\n", "\n")
                neighbors = []
                for match in self.rx_neighbor.finditer(c):
                    chassis_id = match.group("chassis_id")
                    if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                        chassis_id_subtype = 5
                    elif is_mac(chassis_id):
                        chassis_id_subtype = 4
                    else:
                        chassis_id_subtype = 7
                    port_id = match.group("port_id")
                    if is_ipv4(port_id) or is_ipv6(port_id):
                        port_id_subtype = 4
                    elif is_mac(port_id):
                        port_id_subtype = 3
                    else:
                        port_id_subtype = 7
                    caps = 0
                    if match.group("caps").strip():
                        for c in match.group("caps").split():
                            c = c.strip()
                            if c in {"not", "advertised"}:
                                # not caps
                                break
                            if c and (c != "--"):
                                caps |= {
                                    "O": 1,
                                    "P": 2,
                                    "B": 4,
                                    "W": 8,
                                    "R": 16,
                                    "r": 16,
                                    "T": 32,
                                    "C": 64,
                                    "S": 128,
                                }[c]
                    neighbor = {
                        "remote_chassis_id": chassis_id,
                        "remote_chassis_id_subtype": chassis_id_subtype,
                        "remote_port": port_id,
                        "remote_port_subtype": port_id_subtype,
                        "remote_capabilities": caps,
                    }
                    port_descr = match.group("port_descr").strip()
                    system_name = match.group("system_name").strip()
                    system_descr = match.group("system_descr").strip()
                    if bool(port_descr):
                        neighbor["remote_port_description"] = port_descr
                    if bool(system_name):
                        neighbor["remote_system_name"] = system_name
                    if bool(system_descr):
                        neighbor["remote_system_description"] = system_descr
                    neighbors += [neighbor]
                if neighbors:
                    r += [{"local_interface": iface, "neighbors": neighbors}]
        return r
