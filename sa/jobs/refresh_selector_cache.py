# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Refresh selector cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.nosql import get_db
from noc.lib.scheduler.intervaljob import IntervalJob
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.vc.models.vcdomain import VCDomain


class RefreshSelectorCacheJob(IntervalJob):
    name = "sa.refresh_selector_cache"
    cache = "noc.cache.selector"
    initial_submit_interval = 86400
    initial_submit_concurrency = 0
    threaded = True

    def handler(self, *args, **kwargs):
        # Build new cache
        self.info("Building cache")
        r = []
        for s in ManagedObjectSelector.objects.filter(is_enabled=True):
            for o in s.managed_objects:
                r += [
                    {
                        "object": o.id,
                        "selector": s.id,
                        "vc_domain": o.vc_domain
                    }
                ]
        # Write temporary cache
        if r:
            self.info("Writing cache")
            tmp = self.cache + ".tmp"
            c = get_db()[tmp]
            c.insert(r)
            # Substitute cache
            c.rename(self.cache, dropTarget=True)
        else:
            # No data
            self.info("No data to write")
        #
        return True

    @classmethod
    def initial_submit(cls, scheduler, keys):
        if not keys:
            cls.submit(scheduler, interval=86400,
                ts=datetime.datetime.now())
