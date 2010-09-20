# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetLLDPNeighbors
import re

rx_summary_split=re.compile(r"^Device ID.+?\n",re.MULTILINE|re.IGNORECASE)
rx_s_line=re.compile(r"^\S+\s+(?P<local_if>\S+)\s+\d+\s+(?P<capability>\S*)\s+(?P<remote_if>.+)$")
rx_chassis_id=re.compile(r"^Chassis id:\s*(?P<id>\S+)",re.MULTILINE|re.IGNORECASE)
rx_system=re.compile(r"^System Name:\s*(?P<name>\S+)",re.MULTILINE|re.IGNORECASE)


class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_lldp_neighbors"
    implements=[IGetLLDPNeighbors]
    def execute(self):
        r=[]
        v=self.cli("show lldp neighbors")
        v=rx_summary_split.split(v)[1]
        for l in v.splitlines():
            l=l.strip()
            if not l:
                break
            match=rx_s_line.match(l)
            if not match:
                raise Exception("Invalid input: '%s'"%l)
            local_if=match.group("local_if")
            i={"local_interface":local_if, "neighbors": []}
            # Build neighbor data
            n={"remote_port":match.group("remote_if"),"remote_port_subtype":5,"remote_chassis_id_subtype":4}
            # Get capability
            cap=0
            for c in match.group("capability").split(","):
                c=c.strip()
                if c:
                    cap|={
                        "O" : 1, "P" : 2, "B" : 4,
                        "W" : 8, "R" : 16, "T" : 32,
                        "C" : 64, "S" : 128
                    }[c]
            n["remote_capabilities"]=cap
            # Get neighbor detail
            v=self.cli("show lldp neighbors %s detail"%local_if)
            # Get remote chassis id
            match=rx_chassis_id.search(v)
            if not match:
                continue
            n["remote_chassis_id"]=match.group("id")
            match=rx_system.search(v)
            if match:
                n["remote_system_name"]=match.group("name")
            i["neighbors"]+=[n]
            r+=[i]
        return r
