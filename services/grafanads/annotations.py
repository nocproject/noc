#!./bin/python
# ---------------------------------------------------------------------
# annotations handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from time import mktime

import dateutil.parser
import tornado.gen
# Third-party modules
import tornado.web
import ujson
from dateutil import tz
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.archivedalarm import ArchivedAlarm
# NOC modules
from noc.sa.models.managedobject import ManagedObject


class AnnotationsHandler(tornado.web.RequestHandler):
    def initialize(self, service=None):
        self.service = service

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        try:
            req = ujson.loads(self.request.body)
        except ValueError as e:
            raise tornado.web.HTTPError(400, "Bad request")
        #
        f = dateutil.parser.parse(req["range"]["from"], ignoretz=False)
        t = dateutil.parser.parse(req["range"]["to"], ignoretz=False)
        if f > t:
            t, f = f, t
        # Convert from UTC
        t = t.astimezone(tz.tzlocal())
        f = f.astimezone(tz.tzlocal())
        t = t.replace(tzinfo=None)
        f = f.replace(tzinfo=None)
        # Annotation to return in reply
        ra = req.get("annotation")
        #
        result = yield self.service.get_executor("db").submit(
            self.get_annotations, f, t, ra
        )
        self.write(result)

    def get_annotations(self, f, t, annotation):
        # @todo: Check object is exists
        # @todo: Check access
        mo = ManagedObject.get_by_id(int(annotation["query"]))
        r = []
        # Get alarms
        r += self.get_alarms(mo, f, t, annotation)
        r = sorted(r, key=operator.itemgetter("time"))
        return ujson.dumps(r)

    def get_alarms(self, mo, f, t, annotation):
        r = []
        for ac in (ActiveAlarm, ArchivedAlarm):
            q = {
                "managed_object": mo.id
            }
            if ac.status == "A":
                q["timestamp"] = {
                    "$gte": f,
                    "$lte": t
                }
            else:
                q["$or"] = [
                    {
                        "timestamp": {
                            "$gte": f,
                            "$lte": t
                        }
                    },
                    {
                        "clear_timestamp": {
                            "$gte": f,
                            "$lte": t
                        }
                    }
                ]
            c = ac._get_collection()
            for d in c.find(q, {
                "_id": 1,
                "managed_object": 1,
                "alarm_class": 1,
                "timestamp": 1,
                "clear_timestamp": 1
            }):
                if f <= d["timestamp"] <= t:
                    r += [{
                        "annotation": annotation,
                        "time": mktime(d["timestamp"].timetuple()) * 1000 + d["timestamp"].microsecond / 1000,
                        "title": AlarmClass.get_by_id(d["alarm_class"]).name
                        # "tags": X,
                        # "text": X
                    }]
                if "clear_timestamp" in d and f <= d["clear_timestamp"] <= t:
                    r += [{
                        "annotation": annotation,
                        "time": mktime(d["timestamp"].timetuple()) * 1000 + d["timestamp"].microsecond / 1000,
                        "title": "[CLEAR] %s" % AlarmClass.get_by_id(d["alarm_class"]).name
                        # "tags": X,
                        # "text": X
                    }]
        return r
