# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# FM Collector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import time
# NOC modules
from .base import BaseCollector
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.ttsystem import TTSystem


class FMObjectCollector(BaseCollector):
    name = "fm"

    pipeline = [{"$unwind": "$adm_path"},
                {"$group": {"_id": {"adm_path": "$adm_path", "root": "$root"}, "tags": {"$sum": 1}}}
                ]

    pool_mappings = [
        (p.name,
         set(ManagedObject.objects.filter(pool=p).values_list("id", flat=True))) for p in Pool.objects.filter()
    ]

    @staticmethod
    def calc_lag(ts, now):
        if ts and ts < now:
            lag = now - ts
        else:
            lag = 0
        return lag

    def iter_metrics(self):
        db = get_db()
        now = time.time()

        yield ("events_active_total", ), db.noc.events.active.estimated_document_count()
        last_event = db.noc.events.active.find_one(sort=[("timestamp", -1)])
        if last_event:
            # yield ("events_active_first_ts", ), time.mktime(last_event["timestamp"].timetuple())
            yield ("events_active_last_lag_sec",), self.calc_lag(time.mktime(last_event["timestamp"].timetuple()), now)
        yield ("alarms_active_total", ), db.noc.alarms.active.estimated_document_count()
        yield ("alarms_archived_total", ), db.noc.alarms.active.estimated_document_count()
        last_alarm = db.noc.alarms.active.find_one(filter={"timestamp": {"$exists": True}},
                                                   sort=[("timestamp", -1)])
        if last_alarm:
            # yield ("alarms_active_last_ts", ), time.mktime(last_alarm["timestamp"].timetuple())
            yield ("alarms_active_last_lag_sec",), self.calc_lag(time.mktime(last_alarm["timestamp"].timetuple()), now)
        alarms_rooted = set()
        alarms_nroored = set()
        broken_alarms = 0
        for x in db.noc.alarms.active.find({}):
            if "managed_object" not in x:
                broken_alarms += 1
                continue
            if "root" in x:
                alarms_rooted.add(x["managed_object"])
            else:
                alarms_nroored.add(x["managed_object"])
        alarms_all = alarms_rooted.union(alarms_nroored)

        for pool_name, pool_mos in self.pool_mappings:
            yield ("alarms_active_pool_count", ("pool", pool_name)), len(pool_mos.intersection(alarms_all))
            yield ("alarms_active_rooted_pool_count", ("pool", pool_name)), len(pool_mos.intersection(alarms_rooted))
            yield ("alarms_active_nonrooted_pool_count", ("pool", pool_name)), len(pool_mos.intersection(alarms_nroored))
        yield ("alarms_active_broken_count", ), broken_alarms

        for shard in set(TTSystem.objects.filter(is_active=True).values_list("shard_name")):
            yield ("escalation_pool_count", ("shard", shard)), \
                  db["noc.scheduler.escalation.%s" % shard].estimated_document_count()
            first_escalation = db["noc.scheduler.escalator.%s" % shard].find_one(sort=[("ts", -1)])
            if first_escalation:
                # yield ("escalation_last_ts", ("shard", shard)), time.mktime(last_escalation["ts"].timetuple())
                yield ("escalation_first_lag_ts", ("shard", shard)), \
                      self.calc_lag(time.mktime(first_escalation["ts"].timetuple()), now)

            last_escalation = db["noc.scheduler.escalator.%s" % shard].find_one(sort=[("ts", 1)])
            if last_escalation:
                # yield ("escalation_last_ts", ("shard", shard)), time.mktime(last_escalation["ts"].timetuple())
                yield ("escalation_lag_ts", ("shard", shard)), \
                      self.calc_lag(time.mktime(last_escalation["ts"].timetuple()), now)
