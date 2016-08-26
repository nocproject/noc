# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportalarmdetail application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import csv
import tempfile
## Third-party modules
from django.http import HttpResponse
import xlsxwriter
## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter, IntParameter
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.objectpath import ObjectPath
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.object import Object


class ReportAlarmDetailApplication(ExtApplication):
    menu = _("Alarm Detail")
    title = _("Alarm Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    @view("^download/$", method=["GET"], access="launch", api=True,
          validate={
              "from_date": StringParameter(required=True),
              "to_date": StringParameter(required=True),
              "min_duration": IntParameter(required=False),
              "format": StringParameter(choices=["csv", "xlsx"])
          })
    def api_report(self, request, from_date, to_date, format, min_duration=0):
        def row(row, container_path, segment_path):
            def qe(v):
                if v is None:
                    return ""
                if isinstance(v, unicode):
                    return v.encode("utf-8")
                elif isinstance(v, datetime.datetime):
                    return v.strftime("%Y-%m-%d %H:%M:%S")
                elif not isinstance(v, str):
                    return str(v)
                else:
                    return v
            r = [qe(x) for x in row]
            if len(container_path) < self.CONTAINER_PATH_DEPTH:
                container_path += [""] * (self.CONTAINER_PATH_DEPTH - len(container_path))
            else:
                container_path = container_path[:self.CONTAINER_PATH_DEPTH]
            if len(segment_path) < self.SEGMENT_PATH_DEPTH:
                segment_path += [""] * (self.SEGMENT_PATH_DEPTH - len(segment_path))
            else:
                segment_path = segment_path[:self.SEGMENT_PATH_DEPTH]
            return r + container_path + segment_path

        r = [[
            "ID",
            "ROOT_ID",
            "FROM_TS",
            "TO_TS",
            "DURATION_SEC",
            "OBJECT_NAME",
            "OBJECT_ADDRESS",
            "OBJECT_PLATFORM",
            "ALARM_CLASS",
            "OBJECTS",
            "SUBSCRIBERS",
            "TT",
            "ESCALATION_TS"
        ] + ["CONTAINER_%d" % i for i in range(self.CONTAINER_PATH_DEPTH)] + ["SEGMENT_%d" % i for i in range(self.SEGMENT_PATH_DEPTH)]]
        q = {
            "timestamp": {
                "$gte": datetime.datetime.strptime(from_date, "%d.%m.%Y"),
                "$lt": datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
            }
        }
        for a in ArchivedAlarm._get_collection().find(q).sort([("timestamp", 1)]):
            dt = a["clear_timestamp"] - a["timestamp"]
            duration = dt.days * 86400 + dt.seconds
            if duration and duration < min_duration:
                continue
            mo = ManagedObject.get_by_id(a["managed_object"])
            if not mo:
                continue
            path = ObjectPath.get_path(mo)
            if path:
                segment_path = [NetworkSegment.get_by_id(s).name
                                for s in path.segment_path]
                container_path = [Object.get_by_id(s).name for s in path.container_path]
            else:
                segment_path = []
                container_path = []
            r += [row([
                str(a["_id"]),
                str(a["root"]) if a.get("root") else "",
                a["timestamp"],
                a["clear_timestamp"],
                str(duration),
                mo.name,
                mo.address,
                mo.platform,
                AlarmClass.get_by_id(a["alarm_class"]).name,
                sum(ss["summary"] for ss in a["total_objects"]),
                sum(ss["summary"] for ss in a["total_subscribers"]),
                a.get("escalation_tt"),
                a.get("escalation_ts")
            ], container_path, segment_path)]
        if format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=\"alarms.csv\""
            writer = csv.writer(response)
            writer.writerows(r)
            return response
        elif format == "xlsx":
            with tempfile.NamedTemporaryFile(mode="wb") as f:
                wb = xlsxwriter.Workbook(f.name)
                ws = wb.add_worksheet("Alarms")
                for rn, x in enumerate(r):
                    for cn, c in enumerate(x):
                        ws.write(rn, cn, c)
                ws.autofilter(0, 0, rn, cn)
                wb.close()
                response = HttpResponse(content_type="application/x-ms-excel")
                response["Content-Disposition"] = "attachment; filename=\"alarms.xlsx\""
                with open(f.name) as ff:
                    response.write(ff.read())
                return response
