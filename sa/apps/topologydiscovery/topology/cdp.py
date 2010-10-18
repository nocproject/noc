# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CDP Topology Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from base import *

class CDPTopology(Topology):
    ##
    ## Data is [(object,get_topology_data)]
    ##
    def __init__(self,data,hints=[]):
        self.data=data
    ##
    ## Perform CDP topology discovery
    ##
    def discover(self):
        # Build device id -> object mapping
        device_id={} # device id -> object
        for o,d in self.data:
            if d["has_cdp"]:
                device_id[d["cdp_neighbors"]["device_id"]]=o
        # Find links
        links={} # object -> interface -> [(remote_object, remote_interface)]
        for o,d in self.data:
            if not d["has_cdp"]:
                continue
            links[o]={}
            for n in d["cdp_neighbors"]["neighbors"]:
                if n["device_id"] not in device_id:
                    # Outside the topology
                    continue
                if n["local_interface"] not in links[o]:
                    links[o][n["local_interface"]]=[]
                ro=device_id[n["device_id"]]
                links[o][n["local_interface"]]+=[(ro,ro.profile.convert_interface_name(n["remote_interface"]))]
        # Yield links
        for o in links:
            for i in links[o]:
                if len(links[o][i])!=1:
                    # Hub or transparent device between
                    continue
                ro,ri=links[o][i][0]
                # Check reverse mapping exists
                if ri not in links[ro]:
                    continue
                if len(links[ro][ri])!=1:
                    # Hub or transparent device between
                    continue
                lo,li=links[ro][ri][0]
                if lo==o and li==i:
                    yield o,i,ro,ri
    