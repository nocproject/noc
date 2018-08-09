# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Angtel.Topaz.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.lib.validators import is_ipv4, is_ipv6, is_mac


class Script(BaseScript):
    name = "Angtel.Topaz.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_neighbor = re.compile(
        r"^Device ID:(?P<chassis_id>.+)\n"
        r"^Port ID:(?P<port_id>.+)\n"
        r"^Capabilities:(?P<caps>.+)\n"
        r"^System Name:(?P<system_name>.+)\n"
        r"^System description:(?P<system_descr>.+)\n"
        r"^Port description:(?P<port_descr>.+?)\n",
        re.MULTILINE | re.DOTALL
    )
    CAPS = {
        "": 0, "Other": 1, "Repeater": 2,
        "Bridge": 4, "W": 8, "Router": 16,
        "Telephone": 32, "D": 64, "H": 128
    }

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
            v = self.cli("show lldp neighbors %s" % ifname)
            match = self.rx_neighbor.search(v)
            chassis_id = match.group("chassis_id").strip()
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = 5
            elif is_mac(chassis_id):
                chassis_id_subtype = 4
            else:
                chassis_id_subtype = 7
            port_id = match.group("port_id").strip()
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = 4
            elif is_mac(port_id):
                port_id_subtype = 3
            else:
                port_id_subtype = 7
            capabilities = match.group("caps")
            caps = sum([self.CAPS[s.strip()] for s in capabilities.split(",")])
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": caps
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
            r += [{
                "local_interface": ifname,
                "neighbors": [neighbor]
            }]

        return r
