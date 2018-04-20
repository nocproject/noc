# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv managedobject plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin


class ManagedObjectPlugin(InvPlugin):
    name = "managedobject"
    js = "NOC.inv.inv.plugins.managedobject.ManagedObjectPanel"

    def get_data(self, request, o):
        return {
            "id": str(o.id),
            "managed_object_id": o.get_data("management", "managed_object")
        }
