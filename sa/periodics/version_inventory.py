# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Update Managed Object's version info
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.periodic import Task as PeriodicTask

class Task(PeriodicTask):
    """sa.version_inventory periodic task"""
    name = "sa.version_inventory"
    description = "Update managed object's version data"
    default_timeout = 600
    
    def execute(self):
        from noc.sa.models import ReduceTask, ManagedObject
        
        t=ReduceTask.create_task(
            object_selector=ManagedObject.objects.filter(is_managed=True),
            reduce_script="pyrule:version_inventory",
            reduce_script_params={},
            map_script="get_version",
            map_script_params={},
            timeout=self.timeout
        )
        # Wait for task completion
        t.get_result(block=True)
        return True
    
