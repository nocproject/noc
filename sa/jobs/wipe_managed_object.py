# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Wipe managed object
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.wipe.managedobject import wipe
from noc.lib.scheduler.job import Job
from noc.sa.models.managedobject import ManagedObject


class WipeManagedObject(Job):
    name = "sa.wipe_managed_object"
    model = ManagedObject

    def handler(self, *args, **kwargs):
        wipe(self.object)
        return True
