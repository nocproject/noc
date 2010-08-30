# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LLDP Topology Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from base import *

class LLDPTopology(Topology):
    ##
    ## Data is [(object,get_topology_data)]
    ##
    def __init__(self,data,hints=[]):
        self.data=data
    ##
    ## Perform LLDP topology discovery
    ##
    def discover(self):
        # Build chassis id -> object mapping
        chassis_id={} # id->object
        for o,d in self.data:
            if "chassis_id" in d and d["chassis_id"]:
                chassis_id[d["chassis_id"]]=o
        # Get links from LLDP data
        for o,d in self.data:
            if d["has_lldp"]:
                for i in d["lldp_neighbors"]:
                    local_interface=i["local_interface"]
                    for n in i["neighbors"]:
                        rc_id=n["remote_chassis_id"]
                        if rc_id in chassis_id:
                            ro=chassis_id[rc_id] # Resolve to managed object
                            yield (o,local_interface,ro,ro.profile.convert_interface_name(n["remote_port"]))
        