# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3xxx.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
""" 
""" 
import noc.sa.script
from noc.sa.interfaces import IGetChassisID
import re

rx_ver=re.compile(r"^MAC Address\s+:\s*(?P<id>\S+)",re.IGNORECASE|re.MULTILINE)

class Script(noc.sa.script.Script):
    name="DLink.DGS3xxx.get_chassis_id" 
    implements=[IGetChassisID]
    def execute(self):
        v=self.cli("show switch")
        match=rx_ver.search(v)
        return match.group("id")
    
