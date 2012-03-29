# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Update caches
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.periodic import Task as NOCTask


class Task(NOCTask):
    name = "vc.update_cache"
    description = "Update VC caches"

    def execute(self):
        from noc.vc.caches import vcinterfacescount, vcprefixes
        from noc.vc.models import VC

        for vc in VC.objects.all():
            vcinterfacescount.get(vc)
            vcprefixes.get(vc)
        return True
