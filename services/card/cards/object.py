# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Object card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from base import BaseCard
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject

class ObjectCard(BaseCard):
    ''' ObjectCard '''
    name = "object"
    default_template_name = "object"
    model = Object
    
    def get_data(self):
        ''' get_data '''
        # Get path
        path = [{
            "id": self.object.id,
            "name": self.object.name
        }]
        c = self.object.container
        while c:
            c = Object.get_by_id(c)
            if not c:
                break
            if c.name != "Root":
                path.insert(0, {
                    "id": c.id,
                    "name": c.name
                })
            c = c.container
        
        # Get children
        
        children = []
        
        for o in ManagedObject.objects.filter(container=self.object.id):
            children += [{
                "id": o.id,
                "name": o.name,
                "address": o.address,
                "platform": o.platform.name if o.platform else "Unknown",
                "version": o.version.version if o.version else "",
                "description": o.description,
                "object_profile": o.object_profile.id,
                "object_profile_name": o.object_profile.name,
                "segment": o.segment
            }]

        return {
            "object": self.object,
            "path": path,
            "location": self.object.get_data("address", "text"),
            "id": self.object.id,
            "children": children
        }