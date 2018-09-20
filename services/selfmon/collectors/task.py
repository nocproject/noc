# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Task Collector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import datetime
import six
from collections import OrderedDict
# NOC modules
from .base import BaseCollector
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.core.scheduler.job import Job


class TaskObjectCollector(BaseCollector):
    name = "task"
    db = get_db()
    schedulers = [("scheduler", []),
                  ("discovery", Pool.objects.all().order_by("name").values_list("name"))]  # Schedulers (name, shards)

    def __init__(self, service):
        self.schedulers_list = self.load_discovery()
        super(TaskObjectCollector, self).__init__(service)

    def load_discovery(self):
        r = OrderedDict()
        for name, shard in self.schedulers:
            if shard:
                for s in shard:
                    r["noc.schedules.%s.%s" % (name, s)] = {"name": name, "shard": s}
            else:
                r["noc.schedules.%s" % name] = {"name": name}
        return r

    def iter_metrics(self):
        now = datetime.datetime.now() - datetime.timedelta(seconds=5)
        late_q = {
            Job.ATTR_STATUS: Job.S_WAIT,
            Job.ATTR_TS: {
                "$lt": now
            }
        }
        exp_q = {
            Job.ATTR_LAST_STATUS: Job.E_EXCEPTION,
        }
        for scheduler_name, data in six.iteritems(self.schedulers_list):
            sc = self.db[scheduler_name]
            # Calculate late tasks
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
            late_count = sc.count_documents(late_q)

            yield ("task_pool_total",
                   ("scheduler_name", data["name"]),
                   ("pool", data.get("shard", ""))), sc.estimated_document_count()
            yield ("task_exception_count",
                   ("scheduler_name", data["name"]),
                   ("pool", data.get("shard", ""))), sc.count_documents(exp_q)
            yield ("task_running_count",
                   ("scheduler_name", data["name"]),
                   ("pool", data.get("shard", ""))), sc.count_documents({Job.ATTR_STATUS: Job.S_RUN})
            yield ("task_late_count",
                   ("scheduler_name", data["name"]),
                   ("pool", data.get("shard", ""))), late_count
            yield ("task_lag_seconds",
                   ("scheduler_name", data["name"]),
                   ("pool", data.get("shard", ""))), lag
            yield ("task_box_time_avg_seconds",
                   ("scheduler_name", data["name"]),
                   ("pool", data.get("shard", ""))), ldur[0]["avg"] if ldur and ldur[0]["avg"] is not None else 0
            yield ("task_periodic_time_avg_seconds",
                   ("scheduler_name", data["name"]),
                   ("pool", data.get("shard", ""))), \
                ldur[1]["avg"] if len(ldur) > 1 and ldur[0]["avg"] is not None else 0
