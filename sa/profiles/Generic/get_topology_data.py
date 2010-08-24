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
    def execute(self,get_mac=False):
        print get_mac
        data={
            "has_mac": False,
            "mac"    : {},
        }
        if get_mac and self.scripts.has_script("get_mac_address_table"):
            mac_data=self.scripts.get_mac_address_table()
            if mac_data:
                data["has_mac"]=True
                data["mac"]=mac_data
        return data

