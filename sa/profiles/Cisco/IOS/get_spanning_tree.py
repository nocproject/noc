# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetSpanningTree
from noc.lib.text import parse_table
import re

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_spanning_tree"
    implements=[IGetSpanningTree]
    ##
    ## MSTP Parsing
    ##
    rx_mstp_region=re.compile(r"Name\s+\[(?P<region>\S+)\].+Revision\s+(?P<revision>\d+)",re.DOTALL|re.MULTILINE|re.IGNORECASE)
    rx_mstp_instance=re.compile(r"^\s*(\d+)\s+(\S+)",re.MULTILINE)
    rx_mstp_bridge=re.compile("Bridge\s+address\s+(?P<bridge_id>\S+)\s+priority\s+(?P<bridge_priority>\d+).+?Root\s+address\s+(?P<root_id>\S+)\s+priority\s+(?P<root_priority>\d+)",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    rx_mstp_interfaces=re.compile(r"^(?P<interface>\S+)\s+of\s+MST(?P<instance_id>\d+)\s+is\s+(?P<role>\S+)\s+(?P<status>\S+).+?"
        r"Port\s+info\s+port\s+id\s+(?P<port_id>\S+)\s+priority\s+(?P<priority>\d+)\s+cost\s+(?P<cost>\d+).+?"
        r"Designated\s+bridge\s+address\s+(?P<designated_bridge_id>\S+)\s+priority\s+(?P<designated_bridge_priority>\d+)\s+port\s+id\s+(?P<designated_port_id>\S+)",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    def process_mstp(self,cli_stp):
        # Save port settings
        ports={} # instance -> port -> settings
        for I in cli_stp.split("\nMST")[1:]:
            instance_id,_=I.split("\n",1)
            instance_id=int(instance_id)
            ports[instance_id]={}
            for R in parse_table(I):
                interface=self.profile.convert_interface_name(R[0])
                settings=R[-1]
                ports[instance_id][interface]=settings
        #
        v=self.cli("show spanning-tree mst configuration")
        match=self.rx_mstp_region.search(v)
        r={
            "mode"      : "MSTP",
            "instances" : [],
            "configuration" : {
                "MSTP" : {
                    "region"   : match.group("region"),
                    "revision" : match.group("revision"),
                }
            }
        }
        iv={} # instance -> vlans
        for instance,vlans in self.rx_mstp_instance.findall(v):
            iv[instance]=vlans
        #
        interfaces={}
        for I in self.cli("show spanning-tree mst detail").split("\n##### MST")[1:]:
            instance_id,_=I.split(" ",1)
            match=self.rx_mstp_bridge.search(I)
            r["instances"]+=[{
                "id"              : int(instance_id),
                "vlans"           : iv[instance_id],
                "root_id"         : match.group("root_id"),
                "root_priority"   : match.group("root_priority"),
                "bridge_id"       : match.group("bridge_id"),
                "bridge_priority" : match.group("bridge_priority"),
            }]
            for match in self.rx_mstp_interfaces.finditer(I):
                instance_id=int(match.group("instance_id"))
                if instance_id not in interfaces:
                    interfaces[instance_id]=[]
                interface=self.profile.convert_interface_name(match.group("interface"))
                settings=ports[instance_id].get(interface,"").lower()
                print interface,settings
                interfaces[instance_id]+=[{
                    "interface" : interface,
                    "status"    : {"forwarding":"FWD","blocked":"BLK","disabled":"DIS"}[match.group("status")],
                    "port_id"   : match.group("port_id"),
                    "priority"  : match.group("priority"),
                    "cost"      : match.group("cost"),
                    "designated_bridge_id"       : match.group("designated_bridge_id"),
                    "designated_bridge_priority" : match.group("designated_bridge_priority"),
                    "designated_port_id"         : match.group("designated_port_id"),
                    "role"      : {"designated":"DESG","root":"ROOT"}[match.group("role").lower()],
                    "link_type" : "P2P" if "p2p" in settings else "P2P",
                    "edge"      : "edge" in settings,
                }]
        for I in r["instances"]:
            I["interfaces"]=interfaces[I["id"]]
        return r
        
    def execute(self):
        v=self.cli("show spanning-tree")
        if "Spanning tree enabled protocol mstp" in v:
            return self.process_mstp(v)