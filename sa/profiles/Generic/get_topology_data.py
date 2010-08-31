# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_topology_data
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetTopologyData
##
## Retrieve data for topology discovery
##
class Script(noc.sa.script.Script):
    name="Generic.get_topology_data"
    implements=[IGetTopologyData]
    requires=[]
    def execute(self,get_mac=False,get_lldp=False):
        print get_mac
        data={
            "has_mac" : False,
            "mac"     : [],
            "has_lldp": False,
            "lldp_neighbors" : [],
            "portchannels"   : [],
        }
        # get mac addresses
        if get_mac and self.scripts.has_script("get_mac_address_table"):
            mac_data=self.scripts.get_mac_address_table()
            if mac_data:
                data["has_mac"]=True
                data["mac"]=mac_data
        # get lldp neighbors
        if get_lldp:
            if self.scripts.has_script("get_chassis_id"):
                data["chassis_id"]=self.scripts.get_chassis_id()
            if self.scripts.has_script("get_lldp_neighbors"):
                lldp_neighbors=self.scripts.get_lldp_neighbors()
                if lldp_neighbors:
                    data["has_lldp"]=True
                    data["lldp_neighbors"]=lldp_neighbors
        # get portchannels
        if self.scripts.has_script("get_portchannel"):
            data["portchannels"]=self.scripts.get_portchannel()
        return data

