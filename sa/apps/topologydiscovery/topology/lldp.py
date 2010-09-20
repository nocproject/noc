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
        chassis_id={} # id->object
        local_id={} # object -> local -> interface name
        # Build mappings
        for o,d in self.data:
            # chassis id mapping
            if "chassis_id" in d and d["chassis_id"]:
                chassis_id[d["chassis_id"]]=o
            # local interface id mapping
            if d["has_lldp"]:
                for i in d["lldp_neighbors"]:
                    if "local_interface_id" in i:
                        if o not in local_id:
                            local_id[o]={}
                        local_id[o][i["local_interface_id"]]=i["local_interface"]
        # Get links from LLDP data
        for o,d in self.data:
            if d["has_lldp"]:
                for i in d["lldp_neighbors"]:
                    local_interface=i["local_interface"]
                    for n in i["neighbors"]:
                        rc_id=n["remote_chassis_id"]
                        if rc_id in chassis_id:
                            ro=chassis_id[rc_id] # Resolve to managed object
                            if n["remote_port_subtype"]==5: # interfaceName(5)
                                yield (o,local_interface,ro,ro.profile.convert_interface_name(n["remote_port"]))
                            elif n["remote_port_subtype"] in (3,4,7): # macAddress(3) or networkAddress(4) or local(7)
                                rp=n["remote_port"]
                                if n["remote_port_subtype"]==7: # local(7)
                                    rp=int(rp)
                                if ro in local_id and rp in local_id[ro]:
                                    yield (o,local_interface,ro,local_id[ro][rp])
