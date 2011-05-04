# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.get_objects_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetObjectsStatus


class Script(noc.sa.script.Script):
    name="NOC.SAE.get_objects_status"
    implements=[IGetObjectsStatus]
    
    def execute(self, objects=None):
        if objects is None:
            # Get all active objects
            from noc.sa.models import ManagedObject
            
            objects = ManagedObject.objects.filter(is_managed=True).values_list("id", flat=True)
        
        print self.sae.object_status
        return [{"object_id": i, "status": self.sae.object_status.get(i, None)}
                for i in objects]
