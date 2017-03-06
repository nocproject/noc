# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.base import (IntParameter,
                                    MACAddressParameter,
                                    InterfaceTypeError)
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Juniper.JUNOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    ##
    ## EX Series
    ##
    rx_localport = re.compile(r"^(\S+?)\s+?(\d+?)\s+?\S+?\s+?Up.+?$",
        re.MULTILINE | re.DOTALL)
    rx_neigh = re.compile(r"^(?P<local_if>.e-\S+?|me0|fxp0)\s.*?$",
        re.MULTILINE | re.IGNORECASE)
    # If <p_type>=='Interface alias', then <p_id> will match 'Port description'
    # else it will match 'Port ID'
    rx_detail = [
         r"Chassis ID\s+:\s(?P<id>\S+)",
         r"Port type\s+:\s(?P<p_type>.+)",
         r"Port \S+\s+:\s(?P<p_id>.+)",
         r"System name\s+:\s(?P<name>\S+)",
         r"System capabilities",
         r"Supported\s*:\s(?P<capability>.+)"
    ]
    rx_detail1 = [
         r"Chassis ID\s+:\s(?P<id>\S+)",
         r"Port type\s+:\s(?P<p_type>.+)",
         r"Port \S+\s+:\s(?P<p_id>.+)",
         r"System name\s+:\s(?P<name>\S+)"
    ]
    rx_detail2 = [
         r"Chassis ID\s+:\s(?P<id>\S+)",
         r"Port type\s+:\s(?P<p_type>.+)",
         r"Port \S+\s+:\s(?P<p_id>.+)"
    ]

    # Match mx, ex and qfx
    @BaseScript.match(platform__regex="[em]x|qfx")
    def execute_ex(self):
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
            v = self.cli("show lldp neighbors interface %s" % \
                i["local_interface"])
            match = self.match_lines(self.rx_detail, v)
            n = {"remote_chassis_id_subtype": 4}
            if match:
                n["remote_port_subtype"] = {
                    "Interface alias": 1,
                    "Port component": 2,
                    "Mac address": 3,
                    "Interface name": 5,
                    "Locally assigned": 7
                }[match.get("p_type")]
                if n["remote_port_subtype"] == 3:
                    remote_port = \
                        MACAddressParameter().clean(match.get("p_id"))
                elif n["remote_port_subtype"] == 7:
                    p_id = match.get("p_id")
                    try:
                        remote_port = IntParameter().clean(p_id)
                    except InterfaceTypeError:
                        remote_port = p_id
                else:
                    remote_port = match.get("p_id")
                n["remote_chassis_id"] = match.get("id")
                n["remote_system_name"] = match.get("name")
                n["remote_port"] = str(remote_port)
                # Get capability
                cap = 0
                if match.get("capability"):
                    s = match.get("capability")
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
            else:
                match = self.match_lines(self.rx_detail1, v)
                if match:
                    n["remote_port_subtype"] = {
                        "Interface alias": 1,
                        "Port component": 2,
                        "Mac address": 3,
                        "Interface name": 5,
                        "Locally assigned": 7
                    }[match.get("p_type")]
                    if n["remote_port_subtype"] == 3:
                        remote_port = \
                            MACAddressParameter().clean(match.get("p_id"))
                    elif n["remote_port_subtype"] == 7:
                        p_id = match.get("p_id")
                        try:
                            remote_port = IntParameter().clean(p_id)
                        except InterfaceTypeError:
                            remote_port = p_id
                    else:
                        remote_port = match.get("p_id")
                    n["remote_chassis_id"] = match.get("id")
                    n["remote_system_name"] = match.get("name")
                    n["remote_port"] = str(remote_port)
                else:
                    match = self.match_lines(self.rx_detail2, v)
                    if match:
                        n["remote_port_subtype"] = {
                            "Interface alias": 1,
                            "Port component": 2,
                            "Mac address": 3,
                            "Interface name": 5,
                            "Locally assigned": 7
                        }[match.get("p_type")]
                        if n["remote_port_subtype"] == 3:
                            remote_port = \
                                MACAddressParameter().clean(match.get("p_id"))
                        elif n["remote_port_subtype"] == 7:
                            p_id = match.get("p_id")
                            try:
                                remote_port = IntParameter().clean(p_id)
                            except InterfaceTypeError:
                                remote_port = p_id
                        else:
                            remote_port = match.get("p_id")
                        n["remote_chassis_id"] = match.get("id")
                        n["remote_port"] = str(remote_port)
            i["neighbors"] += [n]
            r += [i]
        for q in r:
            if q['local_interface'].endswith(".0"):
                q['local_interface'] = q['local_interface'][:-2]
        return r

    ##
    ## No lldp on M/T
    ##
    @BaseScript.match()
    def execute_other(self):
        raise self.NotSupportedError()
