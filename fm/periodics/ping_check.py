# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Runs PING probe of all hosts
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.lib.periodic

def reduce_ping(task):
    """Reduce script for ping_check"""
    for mt in task.maptask_set.all():
        if mt.status == "C":
            return True
    return False


class Task(noc.lib.periodic.Task):
    name="fm.ping_check"
    description=""
    default_timeout = 30
    
    def execute(self):
        from noc.sa.models import Activator, ReduceTask
        
        # Look for addresses
        params=[]
        for a in Activator.objects.filter(is_active=True):
            objects=[o.trap_source_ip for o in a.managedobject_set.filter(trap_source_ip__isnull=False, is_managed=True)]
            if objects:
                params += [{"activator_name": a.name, "addresses": objects}]
        # Run task
        if params:
            task = ReduceTask.create_task("SAE", reduce_ping, {},
                ["ping_check"] * len(params), params, self.timeout - 1)
            return task.get_result(block=True)
        return True
    
