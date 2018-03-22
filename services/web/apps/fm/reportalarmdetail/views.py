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
import StringIO
import xlsxwriter
import bson
from pymongo import ReadPreference
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter, IntParameter
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.objectpath import ObjectPath
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.object import Object
from noc.services.web.apps.sa.reportobjectdetail.views import ReportObjectAttributes
from noc.services.web.apps.sa.reportobjectdetail.views import ReportAttrResolver
from noc.services.web.apps.sa.reportobjectdetail.views import ReportContainer
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _

class ReportAlarmDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Alarm Detail")
    title = _("Alarm Detail")

    # %fixme make configurable ?
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
              "selector": StringParameter(required=False),
              "ex_selector": StringParameter(required=False),
              "columns": StringParameter(required=False),
              "format": StringParameter(choices=["csv", "xlsx"])
          })
    def api_report(self, request, from_date, to_date, format,
                   min_duration=0, max_duration=0, min_objects=0, min_subscribers=0,
                   segment=None, administrative_domain=None, selector=None,
                   ex_selector=None, columns=None, source="both"):
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
            "object_profile",
            "object_admdomain",
            "object_platform",
            "object_version",
            "alarm_class",
            "objects",
            "subscribers",
            "tt",
            "escalation_ts",
            "container_address"
        ] + ["container_%d" % i for i in range(self.CONTAINER_PATH_DEPTH)] + [
            "segment_%d" % i for i in range(self.SEGMENT_PATH_DEPTH)]

        header_row = [
         "ID",
         _("ROOT_ID"),
         _("FROM_TS"),
         _("TO_TS"),
         _("DURATION_SEC"),
         _("OBJECT_NAME"),
         _("OBJECT_ADDRESS"),
         _("OBJECT_PROFILE"),
         _("OBJECT_ADMDOMAIN"),
         _("OBJECT_PLATFORM"),
         _("OBJECT_VERSION"),
         _("ALARM_CLASS"),
         _("OBJECTS"),
         _("SUBSCRIBERS"),
         _("TT"),
         _("ESCALATION_TS"),
         _("CONTAINER_ADDRESS")
        ] + ["CONTAINER_%d" % i for i in range(self.CONTAINER_PATH_DEPTH)] + [
            "SEGMENT_%d" % i for i in range(self.SEGMENT_PATH_DEPTH)]

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

        mos = ManagedObject.objects.filter(is_managed=True)

        if segment:
            try:
                q["segment_path"] = bson.ObjectId(segment)
            except bson.errors.InvalidId:
                pass

        if administrative_domain:
            administrative_domain = [int(administrative_domain)]
            ads = AdministrativeDomain.get_nested_ids(administrative_domain[0])
            mos = mos.filter(administrative_domain__in=ads)

        if not request.user.is_superuser:
            user_ads = UserAccess.get_domains(request.user)
            mos = mos.filter(
                administrative_domain__in=user_ads)
            if administrative_domain:
                if administrative_domain[0] not in user_ads:
                    administrative_domain = user_ads
            else:
                administrative_domain = user_ads
        if selector:
            selector = ManagedObjectSelector.get_by_id(int(selector))
            mos = mos.filter(selector.Q)
        if ex_selector:
            ex_selector = ManagedObjectSelector.get_by_id(int(ex_selector))
            mos = mos.exclude(ex_selector.Q)

        # Working if Administrative domain set
        if administrative_domain:
            try:
                q["adm_path"] = {"$in": administrative_domain}
                # @todo More 2 level hierarhy
            except bson.errors.InvalidId:
                pass

        mos_id = list(mos.values_list("id", flat=True))
        if selector or ex_selector:
            q["managed_object"] = {"$in": mos_id}

        container_lookup = ReportContainer(mos_id)
        attr = ReportObjectAttributes([])
        attr_res = ReportAttrResolver([])
        if source in ["archive", "both"]:
            # Archived Alarms
            for a in ArchivedAlarm._get_collection().with_options(
                    read_preference=ReadPreference.SECONDARY_PREFERRED).find(q).sort(
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
                    mo.profile.name,
                    mo.administrative_domain.name,
                    attr_res[mo.id][2] if attr else "",
                    attr_res[mo.id][3] if attr else "",
                    AlarmClass.get_by_id(a["alarm_class"]).name,
                    total_objects,
                    total_subscribers,
                    a.get("escalation_tt"),
                    a.get("escalation_ts"),
                    container_lookup[mo.id].get("text", "") if container_lookup else ""
                ], container_path, segment_path), cmap)]
        # Active Alarms
        if source in ["active", "both"]:
            for a in ActiveAlarm._get_collection().with_options(
                    read_preference=ReadPreference.SECONDARY_PREFERRED).find(q).sort(
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
                    mo.profile.name,
                    mo.administrative_domain.name,
                    attr_res[mo.id][2] if attr else "",
                    attr_res[mo.id][3] if attr else "",
                    AlarmClass.get_by_id(a["alarm_class"]).name,
                    total_objects,
                    total_subscribers,
                    a.get("escalation_tt"),
                    a.get("escalation_ts"),
                    container_lookup[mo.id].get("text", ""),
                ], container_path, segment_path), cmap)]

        if format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"alarms.csv\""
            writer = csv.writer(response)
            writer.writerows(r)
            return response
        elif format == "xlsx":
            response = StringIO.StringIO()
            wb = xlsxwriter.Workbook(response)
            ws = wb.add_worksheet("Alarms")
            for rn, x in enumerate(r):
                for cn, c in enumerate(x):
                    ws.write(rn, cn, c)
            ws.autofilter(0, 0, rn, cn)
            wb.close()
            response.seek(0)
            response = HttpResponse(response.getvalue(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "attachment; filename=\"alarms.xlsx\""
            response.close()
            return response
