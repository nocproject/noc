# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Runs PING probe of all hosts
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
import datetime,logging

class Task(noc.sa.periodic.Task):
    name="fm.ping_check"
    description=""
    
    def execute(self):
        from noc.sa.models import Activator
        
        for a in Activator.objects.filter(is_active=True):
            objects=[o.trap_source_ip for o in a.managedobject_set.filter(trap_source_ip__isnull=False,is_managed=True)]
            if objects:
                self.sae.ping_check(a,objects)
        return True

