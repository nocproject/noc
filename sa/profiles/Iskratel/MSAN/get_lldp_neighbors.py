# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MSAN.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Iskratel.MSAN.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_remote = re.compile(
        r"^Chassis ID Subtype: (?P<chassis_id_subtype>.+)\n"
        r"^Chassis ID: (?P<chassis_id>.+)\n"
        r"^Port ID Subtype: (?P<port_id_subtype>.+)\n"
        r"^Port ID: (?P<port_id>.+)\n"
        r"^System Name:(?P<system_name>.*)\n"
        r"^System Description:(?P<system_description>.*)\n"
        r"^Port Description:(?P<port_description>.*)\n"
        r"^System Capabilities Supported:.*\n"
        r"^System Capabilities Enabled:(?P<system_capabilities>.*?)\n",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp remote-device all")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        t = parse_table(v, allow_wrap=True)
        for i in t:
            interface = i[0]
            c = self.cli("show lldp remote-device detail %s" % interface)
            match = self.rx_remote.search(c)
            if match:
                n = {}
                n["remote_chassis_id_subtype"] = {
                    "Chassis Component": 1,
                    "Interface Alias": 2,
                    "Port Component": 3,
                    "MAC Address": 4,
                    "Network Address": 5,
                    "Interface Name": 6,
                    "Local": 7
                }[match.group("chassis_id_subtype").strip()]
                n["remote_chassis_id"] = match.group("chassis_id").strip()
                n["remote_port_subtype"] = {
                    "Interface Alias": 1,
                    "Port Component": 2,
                    "MAC Address": 3,
                    "Network Address": 4,
                    "Interface Name": 5,
                    "Local": 7
                }[match.group("port_id_subtype").strip()]
                n["remote_port"] = match.group("port_id").strip()
                if match.group("port_description").strip():
                    n["remote_port_description"] = \
                        match.group("port_description").strip()
                if match.group("system_name").strip():
                    n["remote_system_name"] = \
                        match.group("system_name").strip()
                if match.group("system_description").strip():
                    n["remote_system_description"] = \
                        match.group("system_description").strip()
                caps = 0
                for c in match.group("system_capabilities").split(","):
                    c = c.strip()
                    if not c:
                        break
                    caps |= {
                        "repeater": 2,
                        "bridge": 4,
                        "router": 16,
                    }[c]
                n["remote_capabilities"] = caps
                r += [{
                    "local_interface": interface,
                    "neighbors": [n]
                }]
        return r
