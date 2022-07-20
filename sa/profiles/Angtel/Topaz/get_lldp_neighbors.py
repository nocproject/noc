# ---------------------------------------------------------------------
# Angtel.Topaz.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.core.text import parse_table
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_ipv4, is_ipv6, is_mac
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
    name = "Angtel.Topaz.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    always_prefer = "S"

    rx_neighbor = re.compile(
        r"^Device ID:(?P<chassis_id>.+)\n"
        r"^Port ID:(?P<port_id>.+)\n"
        r"^Capabilities:(?P<caps>.+)\n"
        r"^System Name:(?P<system_name>.+)\n"
        r"^System description:(?P<system_descr>.+)\n"
        r"^Port description:(?P<port_descr>.+?)\n",
        re.MULTILINE | re.DOTALL,
    )

    def execute_cli(self):
        r = []
        data = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        v = v.replace("\n\n", "\n")
        for l in parse_table(v):
            if not l[0]:
                data[-1] = [s[0] + s[1] for s in zip(data[-1], l)]
                continue
            data += [l]

        for d in data:
            try:
                ifname = self.profile.convert_interface_name(d[0])
            except ValueError:
                continue
            v = self.cli(f"show lldp neighbors {ifname}")
            match = self.rx_neighbor.search(v)
            chassis_id = match.group("chassis_id").strip()
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
            port_id = match.group("port_id").strip()
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_MAC
            else:
                port_id_subtype = LLDP_PORT_SUBTYPE_LOCAL
            caps = lldp_caps_to_bits(
                match.group("caps").strip().split(","),
                {
                    "other": LLDP_CAP_OTHER,
                    "repeater": LLDP_CAP_REPEATER,
                    "bridge": LLDP_CAP_BRIDGE,
                    "wlan-access-point": LLDP_CAP_WLAN_ACCESS_POINT,
                    "router": LLDP_CAP_ROUTER,
                    "telephone": LLDP_CAP_TELEPHONE,
                    "d": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                    "h": LLDP_CAP_STATION_ONLY,
                },
            )
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps,
            }
            system_name = match.group("system_name").strip()
            if system_name:
                neighbor["remote_system_name"] = system_name
            system_descr = match.group("system_descr").strip()
            if system_descr:
                neighbor["remote_system_description"] = system_descr
            port_descr = match.group("port_descr").strip()
            if port_descr:
                neighbor["remote_port_description"] = port_descr
            r += [{"local_interface": ifname, "neighbors": [neighbor]}]

        return r
