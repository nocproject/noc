# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.monitor application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import itertools
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.lib.nosql import get_db
from noc.lib.dateutils import humanize_timedelta


class FMMonitorApplication(ExtApplication):
    """
    fm.monitor application
    """
    title = "FM Monitor"
    menu = "FM Monitor"

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
        archived_alarms = db.noc.alarms.archive.count()
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
