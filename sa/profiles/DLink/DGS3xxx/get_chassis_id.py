# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3xxx.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
##
## DLink.DGS3xxx.get_chassis_id
##
class Script(NOCScript):
    name="DLink.DGS3xxx.get_chassis_id" 
    cache=True
    
    rx_ver=re.compile(r"^MAC Address\s+:\s*(?P<id>\S+)",re.IGNORECASE|re.MULTILINE)
    implements=[IGetChassisID]
    def execute(self):
        v=self.cli("show switch")
        match=self.re_search(self.rx_ver, v)
        return match.group("id")
    
