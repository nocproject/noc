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
from noc.lib.dateutils import humanize_timedelta
from noc.main.models.pool import Pool


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
            t0 = sc.find(limit=1, sort=[("ts", 1)])[0]
            if t0 and t0["ts"] < now:
                lag = humanize_timedelta(
                    now - t0["ts"]
                )
            else:
                lag = "-"
            r += [{
                "pool": p.name,
                "total_tasks": sc.count(),
                "late_tasks": sc.find({"ts": {"$lt": now}}).count(),
                "lag": lag
            }]
        return r
