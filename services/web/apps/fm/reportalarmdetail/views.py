# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.reportalarmdetail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import csv
import tempfile
# Third-party modules
from django.http import HttpResponse
import xlsxwriter
import bson
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter, IntParameter
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.objectpath import ObjectPath
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.object import Object
from noc.services.web.apps.sa.reportobjectdetail.views import ReportObjectAttributes


class ReportAlarmDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Alarm Detail")
    title = _("Alarm Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    @view("^download/$", method=["GET"], access="launch", api=True,
          validate={
              "from_date": StringParameter(required=True),
              "to_date": StringParameter(required=True),
              "min_duration": IntParameter(required=False),
              "max_duration": IntParameter(required=False),
              "min_objects": IntParameter(required=False),
              "min_subscribers": IntParameter(required=False),
              "source": StringParameter(required=True),
              "segment": StringParameter(required=False),
              "administrative_domain": StringParameter(required=False),
              "columns": StringParameter(required=False),
              "format": StringParameter(choices=["csv", "xlsx"])
          })
    def api_report(self, request, from_date, to_date, format,
                   min_duration=0, max_duration=0, min_objects=0, min_subscribers=0,
                   segment=None, administrative_domain=None, columns=None, source="both"):
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

        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        cols = [
            "id",
            "root_id",
            "from_ts",
            "to_ts",
            "duration_sec",
            "object_name",
            "object_address",
            "object_platform",
            "object_version",
            "alarm_class",
            "objects",
            "subscribers",
            "tt",
            "escalation_ts"
        ] + ["container_%d" % i for i in range(self.CONTAINER_PATH_DEPTH)] + ["segment_%d" % i for i in range(self.SEGMENT_PATH_DEPTH)]

        header_row = [
         "ID",
         "ROOT_ID",
         "FROM_TS",
         "TO_TS",
         "DURATION_SEC",
         "OBJECT_NAME",
         "OBJECT_ADDRESS",
         "OBJECT_PLATFORM",
         "OBJECT_VERSION",
         "ALARM_CLASS",
         "OBJECTS",
         "SUBSCRIBERS",
         "TT",
         "ESCALATION_TS"
        ] + ["CONTAINER_%d" % i for i in range(self.CONTAINER_PATH_DEPTH)] + ["SEGMENT_%d" % i for i in range(self.SEGMENT_PATH_DEPTH)]

        if columns:
            cmap = []
            for c in columns.split(","):
                try:
                    cmap += [cols.index(c)]
                except ValueError:
                    continue
        else:
            cmap = list(range(len(cols)))

        r = [translate_row(header_row, cmap)]
        q = {
            "timestamp": {
                "$gte": datetime.datetime.strptime(from_date, "%d.%m.%Y"),
                "$lt": datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
            }
        }
        if segment:
            try:
                q["segment_path"] = bson.ObjectId(segment)
            except bson.errors.InvalidId:
                pass
        if administrative_domain:
            try:
                q["adm_path"] = {"$in": [int(administrative_domain)]}
            except bson.errors.InvalidId:
                pass
        attr = ReportObjectAttributes([])
        if source in ["archive", "both"]:
            # Archived Alarms
            for a in ArchivedAlarm._get_collection().find(q).sort(
                    [("timestamp", 1)]):
                dt = a["clear_timestamp"] - a["timestamp"]
                duration = dt.days * 86400 + dt.seconds
                if duration and duration < min_duration:
                    continue
                if duration and max_duration and duration > max_duration:
                    continue
                total_objects = sum(
                    ss["summary"] for ss in a["total_objects"])
                if min_objects and total_objects < min_objects:
                    continue
                total_subscribers = sum(
                    ss["summary"] for ss in a["total_subscribers"])
                if min_subscribers and total_subscribers < min_subscribers:
                    continue
                mo = ManagedObject.get_by_id(a["managed_object"])
                if not mo:
                    continue
                path = ObjectPath.get_path(mo)
                if path:
                    segment_path = [NetworkSegment.get_by_id(s).name
                                    for s in path.segment_path if NetworkSegment.get_by_id(s)]
                    container_path = [Object.get_by_id(s).name for s in
                                      path.container_path if Object.get_by_id(s)]
                else:
                    segment_path = []
                    container_path = []
                r += [translate_row(row([
                    str(a["_id"]),
                    str(a["root"]) if a.get("root") else "",
                    a["timestamp"],
                    a["clear_timestamp"],
                    str(duration),
                    mo.name,
                    mo.address,
                    attr[mo][2] if attr else "",
                    attr[mo][1] if attr else "",
                    AlarmClass.get_by_id(a["alarm_class"]).name,
                    total_objects,
                    total_subscribers,
                    a.get("escalation_tt"),
                    a.get("escalation_ts")
                ], container_path, segment_path), cmap)]
        # Active Alarms
        if source in ["active", "both"]:
            for a in ActiveAlarm._get_collection().find(q).sort(
                    [("timestamp", 1)]):
                dt = datetime.datetime.now() - a["timestamp"]
                duration = dt.days * 86400 + dt.seconds
                if duration and duration < min_duration:
                    continue
                if duration and max_duration and duration > max_duration:
                    continue
                total_objects = sum(
                    ss["summary"] for ss in a["total_objects"])
                if min_objects and total_objects < min_objects:
                    continue
                total_subscribers = sum(
                    ss["summary"] for ss in a["total_subscribers"])
                if min_subscribers and total_subscribers < min_subscribers:
                    continue
                mo = ManagedObject.get_by_id(a["managed_object"])
                if not mo:
                    continue
                path = ObjectPath.get_path(mo)
                if path:
                    segment_path = [NetworkSegment.get_by_id(s).name
                                    for s in path.segment_path if NetworkSegment.get_by_id(s)]
                    container_path = [Object.get_by_id(s).name for s in
                                      path.container_path if Object.get_by_id(s)]
                else:
                    segment_path = []
                    container_path = []
                r += [translate_row(row([
                    str(a["_id"]),
                    str(a["root"]) if a.get("root") else "",
                    a["timestamp"],
                    # a["clear_timestamp"],
                    "",
                    str(duration),
                    mo.name,
                    mo.address,
                    attr[mo][2] if attr else "",
                    attr[mo][1] if attr else "",
                    AlarmClass.get_by_id(a["alarm_class"]).name,
                    total_objects,
                    total_subscribers,
                    a.get("escalation_tt"),
                    a.get("escalation_ts")
                ], container_path, segment_path), cmap)]

        if format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"alarms.csv\""
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
                response = HttpResponse(
                    content_type="application/x-ms-excel")
                response[
                    "Content-Disposition"] = "attachment; filename=\"alarms.xlsx\""
                with open(f.name) as ff:
                    response.write(ff.read())
                return response
