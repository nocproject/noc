# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Update caches
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.vc.caches import vcinterfacescount, vcprefixes
from noc.vc.models import VC


class UpdateCacheJob(AutoIntervalJob):
    name = "vc.update_cache"
    interval = 300

    def handler(self):
        for vc in VC.objects.all():
            vcinterfacescount.get(vc)
            vcprefixes.get(vc)
        return True
