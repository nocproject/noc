#!./bin/python
##----------------------------------------------------------------------
## annotations handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## Third-party modules
import tornado.web
import tornado.gen
import ujson
import dateutil.parser
## NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmclass import AlarmClass


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
        f = dateutil.parser.parse(req["range"]["from"])
        t = dateutil.parser.parse(req["range"]["to"])
        if f > t:
            t, f = f, t
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
        r = sorted(r, key=operator.attrgetter("time"))
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
                q["$or"] =  [
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
                        "time": d["timestamp"].isoformat(),
                        "title": AlarmClass.get_by_id(d["alarm_class"]).name
                        #"tags": X,
                        #"text": X
                    }]
                if "clear_timestamp" in d and f <= d["clear_timestamp"] <= t:
                    r += [{
                        "annotation": annotation,
                        "time": d["timestamp"].isoformat(),
                        "title": "[CLEAR] %s" % AlarmClass.get_by_id(d["alarm_class"]).name
                        #"tags": X,
                        #"text": X
                    }]
        return r
