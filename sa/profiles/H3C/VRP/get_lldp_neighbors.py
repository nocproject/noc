# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors, MACAddressParameter


class Script(NOCScript):
    name = "H3C.VRP.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    ##
    ## No lldp on 3.02 and older
    ##
    @NOCScript.match(version__startswith="3.02")
    def execute_old(self):
        raise self.NotSupportedError()

    ##
    ## Other (3.03 and newer)
    ##
    rx_ifc_line = re.compile(r"\w*LLDP neighbor-information of port \d+\[(?P<local_if>[^\n]+)\]:\n(?P<tail>.*)", re.MULTILINE | re.DOTALL | re.IGNORECASE)

    @NOCScript.match()
    def execute_other(self):
        r = []
        i = {}
        lldp = self.cli("display lldp neighbor")
        while True:
            match = self.rx_ifc_line.search(lldp)
            if not match:
                break
            pre = lldp[:match.start()]
            lldp = match.group("tail")
            if pre:
                if i:
                    i["neighbors"] += [parse_neighbor(pre)]
                    r += [i]
                i = {
                    "local_interface": match.group("local_if"),
                    "neighbors": []
                }
        if lldp:
            i["neighbors"] += [parse_neighbor(lldp)]
            r += [i]
        return r


def parse_neighbor(text):
    rx_ngh_line = re.compile(r"\s+Neighbor[^\n]+\n\s+Update[^\n]+\n(?P<neighbor>.*\n\n)", re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_neigh = re.compile(r"\s+Chassis\s*ID\s*:\s*(?P<id>\S+).*?Port\s*ID\s*(sub)*type\s*:\s*(?P<p_type>[\w\s]+)\n\s+Port\s*ID\s*:\s*(?P<p_id>.+?)\n.+?Sys.*?name\s*:\s*(?P<name>[^\n]+)\n.*?Sys.*?cap.*?enabled\s*:\s*(?P<capability>[^\n]+)", re.MULTILINE | re.IGNORECASE | re.DOTALL)
    n = []
    for match_n in rx_ngh_line.finditer(text):
        for match_data in rx_neigh.finditer(match_n.group("neighbor")):
            n = {"remote_chassis_id_subtype": 4}
            if match_data:
                n["remote_port_subtype"] = {
                    "macAddress": 3,
                    "Interface name": 5,
                    "Locally assigned": 7
                }[match_data.group("p_type")]
                if n["remote_port_subtype"] == 3:
                    n["remote_port"] = MACAddressParameter().clean(match_data.group("p_id"))
                else:
                    n["remote_port"] = match_data.group("p_id")
                n["remote_chassis_id"] = match_data.group("id")
                n["remote_system_name"] = match_data.group("name")
                # Get capability
                cap = 0
                for c in match_data.group("capability").strip().split(","):
                    cap |= {
                        "NA": 0, "Other": 1, "Repeater": 2, "Bridge": 4,
                        "WLAN": 8, "Router": 16, "Telephone": 32,
                        "Cable": 64, "StationOnly": 128
                    }[c]
                n["remote_capabilities"] = cap
    return n
