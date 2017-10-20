# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.lib.validators import is_int, is_ipv4, is_ipv6, is_mac
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MA4000.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_neighbor = re.compile(
        r"^Device ID: (?P<chassis_id>\S+)\s*\n"
        r"^Port ID: (?P<port_id>\S+)\s*\n"
        r"^Time To Live: \S+\s*\n\n"
        r"(^Port description:(?P<port_descr>.*)\n)?"
        r"(^System name:(?P<system_name>.*)\n)?"
        r"(^System description:(?P<system_descr>.*)\n)?"
        r"(\n)?"
        r"^Capabilities:(?P<caps>.*?)\n\n",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        r = []
        t = parse_table(self.cli("show lldp neighbor"), allow_wrap=True)
        for i in t:
            c = self.cli("show lldp neighbor %s" % i[0])
            match = self.rx_neighbor.search(c)
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
            for c in match.group("caps").split(","):
                c = c.strip()
                if c:
                    caps |= {
                        "Other": 1, "Repeater": 2, "Bridge": 4,
                        "Access Point": 8, "Router": 16, "Telephone": 32,
                        "Cable Device": 64, "Station only": 128
                    }[c]
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps
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
            r += [{
                "local_interface": i[0],
                "neighbors": [neighbor]
            }]
        return r
