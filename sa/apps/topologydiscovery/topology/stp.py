# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STP Topology Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from base import *
import pprint

class STPTopology(Topology):
    ##
    ## Data is [(object,get_topology_data)]
    ##
    def __init__(self,data,hints=[]):
        self.data=data
    ##
    ## Perform LLDP topology discovery
    ##
    def discover(self):
        bridges={} # bridge_id -> object
        ports={}   # bridge_id -> port_id -> interface
        stp_data={} # 
        # Build lookup tables
        for o,d in self.data:
            if d["has_stp"] and d["stp"]:
                for I in d["stp"]["instances"]:
                    # Populate bridges map
                    bridge_id=I["bridge_id"]
                    bridges[bridge_id]=o
                    # Populate ports maps
                    if bridge_id not in ports:
                        ports[bridge_id]={}
                        # Enumerate interfaces
                        for i in I["interfaces"]:
                            ports[bridge_id][i["port_id"]]=i["interface"]
        # Enumerate links
        links=set() # (o1,i1,o2,i2)
        for o1,d in self.data:
            if not d["has_stp"] or not d["stp"]:
                continue
            for I in d["stp"]["instances"]:
                bridge_id=I["bridge_id"]
                for i in I["interfaces"]:
                    # Inspect only root ports
                    if i["role"] not in ("root","alternate"): # @todo: master?
                        continue
                    i1=i["interface"]
                    db=i["designated_bridge_id"]
                    i2id=i["designated_port_id"]
                    if db in bridges and i2id in ports[db]:
                        o2=bridges[db]
                        i2=ports[db][i2id]
                        links.add((o1,i1,o2,i2))
        # Yield links
        for o1,i1,o2,i2 in links:
            yield o1,i1,o2,i2
    