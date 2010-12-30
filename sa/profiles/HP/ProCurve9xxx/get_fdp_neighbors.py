# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_fdp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetFDPNeighbors
##
## HP.ProCurve.get_fdp_neighbors
##
class Script(NOCScript):
    name="HP.ProCurve9xxx.get_fdp_neighbors"
    implements=[IGetFDPNeighbors]
    
    rx_split=re.compile(r"^\s*----.+?\n",re.MULTILINE|re.DOTALL)
    def execute(self):
        r=[]
        # Get neighbors
        v=self.cli("show fdp neighbors")
        for l in self.rx_split.split(v)[1].splitlines():
            l=l.strip()
            if not l:
                continue
            data = l.split()
            local_interface = data[1]
            r+=[{"local_interface":local_interface,
                "neighbors":[{ 'remote_capability': data[3],
                                'remote_device_id' : data[0],
                                'remote_platform' : data[4],
                                'remote_port_id' : data[5],
                                'hold_tm' : data[2]
                                  }]}]
        return r
    
