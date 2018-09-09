# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# FM Collector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseCollector
from noc.lib.nosql import get_db
from noc.lib.dateutils import humanize_timedelta
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject


class FMObjectCollector(BaseCollector):
    name = "fm"

    pipeline = [{"$unwind": "$adm_path"},
                {"$group": {"_id": {"adm_path": "$adm_path", "root": "$root"}, "tags": {"$sum": 1}}}
                ]

    pool_mappings = [
        (p.name,
         set(ManagedObject.objects.filter(pool=p).values_list("id", flat=True))) for p in Pool.objects.filter()
    ]

    def iter_metrics(self):
        db = get_db()

        yield ("events_active_total", ), db.noc.events.active.estimated_document_count()
        yield ("events_active_first", ), db.noc.events.new.find_one(sort=[("timestamp", 1)])["timestamp"].isoformat()

        yield ("alarms_active_total", ), db.noc.alarms.active.estimated_document_count()
        yield ("alarms_archived_total", ), db.noc.alarms.active.estimated_document_count()
        yield ("alarms_active_first", ), db.noc.alarms.active.estimated_document_count()

        alarms_rooted = set()
        alarms_nroored = set()
        bad_alarms = 0
        for x in db.noc.alarms.active.find({}):
            if "managed_object" not in x:
                bad_alarms += 1
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
        yield ("alarms_active_bad_count", ), bad_alarms
