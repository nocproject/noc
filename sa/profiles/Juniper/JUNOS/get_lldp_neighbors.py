# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.base import IntParameter
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Juniper.JUNOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    #
    # EX Series
    #
    rx_localport = re.compile(
        r"^(\S+?)\s+?(\d+?)\s+?\S+?\s+?Up.+?$",
        re.MULTILINE | re.DOTALL)
    rx_neigh = re.compile(
        r"^(?P<local_if>.e-\S+?|me\d|fxp0)\s.*?$",
        re.MULTILINE)
    # If <p_type>=='Interface alias', then <p_id> will match 'Port description'
    # else it will match 'Port ID'
    rx_detail = re.compile(
        r"Chassis type\s+:\s+(?P<ch_type>.+)\n"
        r"Chassis ID\s+:\s(?P<id>\S+)\n"
        r"Port type\s+:\s(?P<p_type>.+)\n"
        r"Port ID\s+:\s(?P<p_id>.+)\n"
        r"(Port description\s+:\s(?P<p_descr>.+)\n)?"
        r"(System name\s+:\s(?P<name>.+)\n)?",
        re.MULTILINE
    )
    rx_caps = re.compile(
        r"System capabilities\s*\n"
        r"\s*Supported\s*:\s(?P<capability>.+)\n",
        re.MULTILINE
    )
    CHASSIS_TYPE = {
        "Mac address": 4,
        "Network address": 5
    }
    PORT_TYPE = {
        "Interface alias": 1,
        "Port component": 2,
        "Mac address": 3,
        "Interface name": 5,
        "Locally assigned": 7
    }

    def execute_cli(self):
        if self.is_has_lldp:
            return self.execute_switch()
        else:
            return self.execute_other()

    # Match mx, ex, qfx, acx
    def execute_switch(self):
        r = []
        # Collect data
        local_port_ids = {}  # name -> id
        v = self.cli("show lldp local-information")
        for port, local_id in self.rx_localport.findall(v):
            local_port_ids[port] = IntParameter().clean(local_id)
        v = self.cli("show lldp neighbors")
        ifs = [{
            "local_interface": match.group("local_if"),
            "neighbors": [],
        } for match in self.rx_neigh.finditer(v)]
        for i in ifs:
            if i["local_interface"] in local_port_ids:
                i["local_interface_id"] = local_port_ids[i["local_interface"]]
            v = self.cli(
                "show lldp neighbors interface %s" % i["local_interface"]
            )
            n = {}
            match = self.rx_detail.search(v)
            n["remote_chassis_id_subtype"] = self.CHASSIS_TYPE[
                match.group("ch_type")
            ]
            n["remote_chassis_id"] = match.group("id")
            n["remote_port_subtype"] = self.PORT_TYPE[match.group("p_type")]
            n["remote_port"] = match.group("p_id")
            if match.group("p_descr"):
                n["remote_port_description"] = match.group("p_descr")
            if match.group("name"):
                n["remote_system_name"] = match.group("name")
            # Get capability
            cap = 0
            match = self.rx_caps.search(v)
            if match:
                s = match.group("capability")
                # WLAN Access Point
                s = s.replace(" Access Point", "")
                # Station Only
                s = s.replace(" Only", "")
                for c in s.strip().split(" "):
                    cap |= {
                        "Other": 1, "Repeater": 2, "Bridge": 4,
                        "WLAN": 8, "Router": 16, "Telephone": 32,
                        "Cable": 64, "Station": 128
                    }[c]
                n["remote_capabilities"] = cap
            i["neighbors"] += [n]
            r += [i]
        for q in r:
            if q['local_interface'].endswith(".0"):
                q['local_interface'] = q['local_interface'][:-2]
        return r

    #
    # No lldp on M/T
    #
    def execute_other(self):
        raise self.NotSupportedError()
