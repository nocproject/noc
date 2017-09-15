# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.monitor application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import itertools
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.core.scheduler.job import Job
from noc.core.translation import ugettext as _


class InvMonitorApplication(ExtApplication):
    """
    fm.monitor application
    """
    title = _("Monitor")
    menu = _("Monitor")

    @view(url="^$", method=["GET"], access="read", api=True)
    def api_data(self, request):
        # waiting for https://github.com/influxdata/telegraf/issues/1363
        # to be done
        db = get_db()
        r = {}
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
            exp_q = {
                Job.ATTR_LAST_STATUS: Job.E_EXCEPTION,
            }
            t0 = sc.find_one(late_q, limit=1, sort=[("ts", 1)])
            ldur = list(sc.aggregate([
                {
                    "$group": {
                        "_id": "$jcls",
                        "avg": {"$avg": "$ldur"}
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]))
            if t0 and t0["ts"] < now:
                lag = (now - t0["ts"]).total_seconds()
            else:
                lag = 0
            late_count = sc.find(late_q).count()
            #
            r[p.name.lower()] = {
                "pool": p.name.lower(),
                "total_tasks": sc.count(),
                "exception_tasks": sc.find(exp_q).count(),
                "running_tasks": sc.find({Job.ATTR_STATUS: Job.S_RUN}).count(),
                "late_tasks": late_count,
                "lag": lag,
                "avg_box_tasks": ldur[0]["avg"] if ldur else 0,
                "avg_periodic_tasks": ldur[1]["avg"] if len(ldur) > 1 else 0
            }
        return r
