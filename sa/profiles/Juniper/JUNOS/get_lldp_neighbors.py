# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
import binascii
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors, IntParameter, MACAddressParameter


class Script(NOCScript):
    name = "Juniper.JUNOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]
    ##
    ## EX Series
    ##
    rx_localport = re.compile(r"^(\S+?)\s+?(\d+?)\s+?\S+?\s+?Up.+?$",
        re.MULTILINE | re.DOTALL)
    rx_neigh = re.compile(r"(?P<local_if>.e-\S+?)\s.*?$",
        re.MULTILINE | re.IGNORECASE)
    # If <p_type>=='Interface alias', then <p_id> will match 'Port description'
    # else it will match 'Port ID'
    rx_detail = re.compile(r".*Chassis ID\s+:\s(?P<id>\S+).*?Port type\s+:\s(?P<p_type>[^\n]+).*?Port \S+\s+:\s(?P<p_id>[^\n]+).*?System name\s+:\s(?P<name>\S+).*?System capabilities.+?Supported:\s(?P<capability>[^\n]+).*", re.MULTILINE | re.IGNORECASE | re.DOTALL)

    @NOCScript.match(platform__startswith="ex")
    def execute_ex(self):
        ifs = []
        r = []
        # Collect data
        local_port_ids = {}  # name -> id
        for port, local_id in self.rx_localport.findall(self.cli("show lldp local-information")):
            local_port_ids[port] = IntParameter().clean(local_id)
        v = self.cli("show lldp neighbors")
        for match in self.rx_neigh.finditer(v):
            ifs += [{
                "local_interface": match.group("local_if"),
                "neighbors": [],
            }]
        for i in ifs:
            if i["local_interface"] in local_port_ids:
                i["local_interface_id"] = local_port_ids[i["local_interface"]]
            v = self.cli("show lldp neighbors interface %s" % i["local_interface"])
            match = self.re_search(self.rx_detail, v)
            n = {"remote_chassis_id_subtype": 4}
            if match:
                n["remote_port_subtype"] = {
                    "Mac address": 3,
                    "Interface alias": 5,
                    "Locally assigned": 7
                }[match.group("p_type")]
                if n["remote_port_subtype"] == 3:
                    remote_port = MACAddressParameter().clean(match.group("p_id"))
                elif n["remote_port_subtype"] == 7:
                    remote_port = IntParameter().clean(match.group("p_id"))
                else:
                    remote_port = match.group("p_id")
                n["remote_chassis_id"] = match.group("id")
                n["remote_system_name"] = match.group("name")
                n["remote_port"] = remote_port
                # Get capability
                cap = 0
                for c in match.group("capability").strip().split(" "):
                        cap |= {
                        "Other": 1, "Repeater": 2, "Bridge": 4,
                        "WLAN": 8, "Router": 16, "Telephone": 32,
                        "Cable": 64, "Station": 128
                        }[c]
                n["remote_capabilities"] = cap
            i["neighbors"] += [n]
            r += [i]
        return r

    ##
    ## No lldp on MX
    ##
    @NOCScript.match()
    def execute_other(self):
        raise self.NotSupportedError()
