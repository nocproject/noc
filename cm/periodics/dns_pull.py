# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic

class Task(noc.sa.periodic.Task):
    name="cm.dns_pull"
    description=""
    
    def execute(self):
        from noc.cm.models import DNS
        DNS.global_pull()
        return True
        
