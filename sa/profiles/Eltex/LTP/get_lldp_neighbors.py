# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4, is_ipv6, is_mac
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.LTP.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    CAPS_MAP = {
        "O": 1, "Other": 1,
        "r": 2, "Repeater": 2,
        "B": 4, "Bridge": 4,
        "W": 8, "Access Point": 8,
        "R": 16, "Router": 16,
        "T": 32, "Telephone": 32,
        "C": 64, "Cable Device": 64,
        "S": 128, "Station only": 128,
        "D": 256, "H": 512, "TP": 1024,
    }

    rx_detail = re.compile(
        r"^Port description:(?P<port_descr>.*)\n",
        re.MULTILINE
    )

    def execute_cli(self):
        r = []
        with self.profile.switch(self):
            lldp = self.cli("show lldp neighbors")
            for link in parse_table(lldp, allow_wrap=True):
                local_interface = link[0]
                remote_chassis_id = link[1]
                remote_port = link[2]
                remote_system_name = link[3]
                # Get capability
                cap = 0
                for c in link[4].split(","):
                    c = c.strip()
                    if c:
                        cap |= self.CAPS_MAP[c]

                if (is_ipv4(remote_chassis_id) or is_ipv6(remote_chassis_id)):
                    remote_chassis_id_subtype = 5
                elif is_mac(remote_chassis_id):
                    remote_chassis_id = MACAddressParameter().clean(remote_chassis_id)
                    remote_chassis_id_subtype = 4
                else:
                    remote_chassis_id_subtype = 7

                # Get remote port subtype
                remote_port_subtype = 1
                if is_ipv4(remote_port):
                    # Actually networkAddress(4)
                    remote_port_subtype = 4
                elif is_mac(remote_port):
                    # Actually macAddress(3)
                    # Convert MAC to common form
                    remote_port = MACAddressParameter().clean(remote_port)
                    remote_port_subtype = 3
                elif is_int(remote_port):
                    # Actually local(7)
                    remote_port_subtype = 7
                i = {
                    "local_interface": local_interface,
                    "neighbors": []
                }
                n = {
                    "remote_chassis_id": remote_chassis_id,
                    "remote_chassis_id_subtype": remote_chassis_id_subtype,
                    "remote_port": remote_port,
                    "remote_port_subtype": remote_port_subtype,
                    "remote_capabilities": cap,
                }
                if remote_system_name:
                    n["remote_system_name"] = remote_system_name

                try:
                    c = self.cli("show lldp neighbors interface %s" % local_interface)
                    match = self.rx_detail.search(c)
                    if match:
                        if match.group("port_descr").strip():
                            port_descr = match.group("port_descr").strip()
                            n["remote_port_description"] = port_descr
                except Exception:
                    pass
                i["neighbors"] += [n]
                r += [i]
        return r
