# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.monitor application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import itertools
import operator
from cachetools import TTLCache, cachedmethod
from collections import defaultdict
from django.db import connection
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.lib.nosql import get_db
from noc.lib.dateutils import humanize_timedelta
from noc.core.translation import ugettext as _
from noc.main.models.pool import Pool


class PoolConvert(object):
    """
    Convert PoolID to PoolName.
    """
    def __init__(self):
        self.convert = self.load()

    @staticmethod
    def load():
        return {str(p[0]): p[1] for p in Pool.objects.filter().values_list("id", "name")}

    def __getitem__(self, item):
        return self.convert[item]


class PoolAdConvert(object):
    """
    Administrative Domain that contains Pool
    Use getitem PoolId
    """
    _pool_convert_cache = TTLCache(30, 3600)

    def __init__(self):
        self.convert = self.load()

    @cachedmethod(operator.attrgetter("_pool_convert_cache"))
    def load(self):
        d = defaultdict(list)

        query = "select distinct pool,administrative_domain_id from sa_managedobject"
        cursor = connection.cursor()
        cursor.execute(query)
        out = cursor.fetchall()

        for o in out:
            d[o[0]].append(o[1])

        return d

    def __getitem__(self, item):
        return self.convert[item]

    def __iter__(self):
        return itertools.chain(self.convert)


class FMMonitorApplication(ExtApplication):
    """
    fm.monitor application
    """
    title = _("FM Monitor")
    menu = _("FM Monitor")
    p_c = PoolConvert()
    a_p = PoolAdConvert()

    @view(url="^data/", method=["GET"], access="read", api=True)
    def api_data(self, request):
        db = get_db()
        r = []
        now = datetime.datetime.now()
        # Classifier section
        new_events = db.noc.events.new.count()
        failed_events = db.noc.events.failed.count()
        first_new_event = db.noc.events.new.find_one(sort=[("timestamp", 1)])
        if first_new_event:
            classification_lag = humanize_timedelta(now - first_new_event["timestamp"])
        else:
            classification_lag = "-"
        r += [
            ("classifier", "new_events", new_events),
            ("classifier", "failed_events", failed_events),
            ("classifier", "lag", classification_lag)
        ]
        # Correlator section
        sc = db.noc.schedules.fm.correlator
        dispose = sc.find({"jcls": "dispose"}).count()
        if dispose:
            f = sc.find_one({"jcls": "dispose"}, sort=[("ts", 1)])
            dispose_lag = humanize_timedelta(now - f["ts"])
        else:
            dispose_lag = "-"
        c_jobs = sc.find({"jcls": {"$ne": "dispose"}}).count()
        r += [
            ("correlator", "dispose", dispose),
            ("correlator", "dispose_lag", dispose_lag),
            ("correlator", "jobs", c_jobs)
        ]
        # Stats
        active_events = db.noc.events.active.count()
        archived_events = db.noc.events.archive.count()
        active_alarms = db.noc.alarms.active.count()
        archived_alarms = db.noc.alarms.archived.count()
        r += [
            ("events", "new_events", new_events),
            ("events", "active_events", active_events),
            ("events", "archived_events", archived_events),
            ("events", "failed_events", failed_events),
            ("alarms", "active_alarms", active_alarms),
            ("alarms", "archived_alarms", archived_alarms)
        ]
        # Feed result
        seq = itertools.count()
        return [
            {
                "id": seq.next(),
                "group": g,
                "key": k,
                "value": v
            } for g, k, v in r
        ]

    @view(url="^data2/", method=["GET"], access="read", api=True)
    def api_data2(self, request):
        db = get_db()
        r = {
            "classifier": {},
            "correlator": {},
            "events": {},
            "alarms": {}
        }
        now = datetime.datetime.now()
        # Classifier section
        new_events = db.noc.events.new.count()
        failed_events = db.noc.events.failed.count()
        first_new_event = db.noc.events.new.find_one(sort=[("timestamp", 1)])
        if first_new_event:
            classification_lag = humanize_timedelta(now - first_new_event["timestamp"])
        else:
            classification_lag = "-"
        r["classifier"] = {
            "new_events": new_events,
            "failed_events": failed_events,
            "lag": classification_lag
        }
        # Correlator section
        sc = db.noc.schedules.fm.correlator
        dispose = sc.find({"jcls": "dispose"}).count()
        if dispose:
            f = sc.find_one({"jcls": "dispose"}, sort=[("ts", 1)])
            dispose_lag = humanize_timedelta(now - f["ts"])
        else:
            dispose_lag = "-"
        c_jobs = sc.find({"jcls": {"$ne": "dispose"}}).count()
        r["correlator"] = {
            "dispose": dispose,
            "dispose_lag": dispose_lag,
            "jobs": c_jobs
        }
        # Stats
        active_events = db.noc.events.active.count()
        archived_events = db.noc.events.archive.count()
        active_alarms = db.noc.alarms.active.count()
        archived_alarms = db.noc.alarms.archived.count()
        r["events"] = {
            "new_events": new_events,
            "active_events": active_events,
            "archived_events": archived_events,
            "failed_events": failed_events,
        }
        r["alarms"] = {
            "active_alarms": active_alarms,
            "archived_alarms": archived_alarms
        }
        # Feed result
        return r

    @view(url="^data3/", method=["GET"], access="read", api=True)
    def api_data3(self, request):
        r = {}

        pipeline = [{"$unwind": "$adm_path"},
                    {"$group": {"_id": {"adm_path": "$adm_path", "root": "$root"}, "tags": {"$sum": 1}}}
                    ]

        z = defaultdict(int)
        y = {}
        res = get_db()["noc.alarms.active"].aggregate(pipeline)

        for x in res["result"]:
            if "root" in x["_id"]:
                z[x["_id"]["adm_path"]] += x["tags"]
            else:
                y[x["_id"]["adm_path"]] = x["tags"]

        for e in self.a_p:
            non_root = sum([y[x] for x in self.a_p[e] if x in y])
            w_root = sum([z[x] for x in self.a_p[e] if x in z])
            r[self.p_c[e]] = {"non-root": non_root,
                              "root": w_root,
                              "total": non_root + w_root
                              }

        return r
