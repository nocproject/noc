# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.monitor application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import itertools
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.core.scheduler.job import Job


class InvMonitorApplication(ExtApplication):
    """
    fm.monitor application
    """
    title = "Monitor"
    menu = "Monitor"

    @view(url="^$", method=["GET"], access="read", api=True)
    def api_data(self, request):
        db = get_db()
        r = []
        now = datetime.datetime.now()
        for p in Pool.objects.all().order_by("name"):
            sc = db["noc.schedules.discovery.%s" % p.name]
            # Calculate late tasks
            late_q = {
                Job.ATTR_STATUS: Job.S_WAIT,
                Job.ATTR_TS: {
                    "$lt": now
                }
            }
            t0 = sc.find_one(late_q, limit=1, sort=[("ts", 1)])
            if t0 and t0["ts"] < now:
                lag = str(
                    now - t0["ts"]
                )
            else:
                lag = "-"
            late_count = sc.find(late_q).count()
            #
            r += [{
                "pool": p.name,
                "total_tasks": sc.count(),
                "running_tasks": sc.find({Job.ATTR_STATUS: Job.S_RUN}).count(),
                "late_tasks": late_count,
                "lag": lag
            }]
        return r
