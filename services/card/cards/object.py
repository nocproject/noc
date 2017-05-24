# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Object card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
# NOC modules
from base import BaseCard
from noc.inv.models.object import Object


class ObjectCard(BaseCard):
    name = "object"
    default_template_name = "object"
    model = Object

    def get_data(self):
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
            path.insert(0, {
                "id": c.id,
                "name": c.name
            })
            c = c.container
        # Get children
        children = []
        for o in Object.objects.filter(container=self.object.id):
            children += [{
                "id": o.id,
                "name": o.name,
                "object": o
            }]
        #
        return {
            "object": self.object,
            "path": path,
            "children": children
        }
