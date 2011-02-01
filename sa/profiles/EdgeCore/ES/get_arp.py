# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
""" 
""" 
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re

class Script(NOCScript):
    name="EdgeCore.ES.get_arp" 
    implements=[IGetARP]

    rx_line=re.compile(r"^(?P<ip>\d+\.\S+)\s+(?P<mac>[0-9a-f]\S+)\s+(?P<interface>\S+)\s+", re.IGNORECASE|re.DOTALL|re.MULTILINE)
    def execute(self):
        try:
	    return self.cli("show arp",list_re=self.rx_line)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
