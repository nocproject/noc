# ---------------------------------------------------------------------
# fm.reportalarmcomments application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import csv
import xlsxwriter
import bson
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile

# Third-party modules
from django.http import HttpResponse

# from pymongo import ReadPreference

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.core.comp import smart_text


def get_column_width(name):
    excel_column_format = {
        "ID": 6,
        "OBJECT_NAME": 38,
        "OBJECT_STATUS": 10,
        "OBJECT_PROFILE": 17,
        "OBJECT_PLATFORM": 25,
        "AVAIL": 6,
        "ADMIN_DOMAIN": 25,
        "PHYS_INTERFACE_COUNT": 5,
    }
    if name.startswith("Up") or name.startswith("Down") or name.startswith("-"):
        return 8
    if name.startswith("ADM_PATH"):
        return excel_column_format["ADMIN_DOMAIN"]
    if name in excel_column_format:
        return excel_column_format[name]
    return 15


class ReportAlarmCommentsApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Alarm Comments")
    title = _("Alarm Comments Detail")

    @view(
        "^download/$",
        method=["GET"],
        access="launch",
        api=True,
        validate={
            "from_date": StringParameter(required=True),
            "to_date": StringParameter(required=True),
            "source": StringParameter(required=True),
            "administrative_domain": StringParameter(required=False),
            "alarm_class": StringParameter(required=False),
            "columns": StringParameter(required=False),
            "o_format": StringParameter(choices=["csv", "csv_zip", "xlsx"]),
        },
    )
    def api_report(
        self,
        request,
        from_date,
        to_date,
        o_format,
        administrative_domain=None,
        columns=None,
        source="both",
        alarm_class=None,
        enable_autowidth=False,
    ):
        def row(row):
            def qe(v):
                if v is None:
                    return ""
                if isinstance(v, str):
                    return smart_text(v)
                if isinstance(v, datetime.datetime):
                    return v.strftime("%Y-%m-%d %H:%M:%S")
                if not isinstance(v, str):
                    return smart_text(v)
                return v

            return [qe(x) for x in row]

        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        cols = [
            "id",
            "alarm_class",
            "alarm_from_ts",
            "alarm_to_ts",
            "alarm_tt",
            "object_name",
            "object_address",
            "object_admdomain",
            "log_timestamp",
            "log_source",
            "log_message",
            # "tt",
            # "escalation_ts",
        ]

        header_row = [
            "ID",
            _("ALARM_CLASS"),
            _("ALARM_FROM_TS"),
            _("ALARM_TO_TS"),
            _("ALARM_TT"),
            _("OBJECT_NAME"),
            _("OBJECT_ADDRESS"),
            _("OBJECT_ADMDOMAIN"),
            _("LOG_TIMESTAMP"),
            _("LOG_SOURCE"),
            _("LOG_MESSAGE"),
        ]

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
        fd = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
        match = {
            "timestamp": {"$gte": datetime.datetime.strptime(from_date, "%d.%m.%Y"), "$lte": fd}
        }
        mos = ManagedObject.objects.filter()

        ads = []
        if administrative_domain:
            if administrative_domain.isdigit():
                administrative_domain = [int(administrative_domain)]
                ads = AdministrativeDomain.get_nested_ids(administrative_domain[0])

        if not request.user.is_superuser:
            user_ads = UserAccess.get_domains(request.user)
            if administrative_domain and ads:
                if administrative_domain[0] not in user_ads:
                    ads = list(set(ads) & set(user_ads))
                    if not ads:
                        return HttpResponse(
                            "<html><body>Permission denied: Invalid Administrative Domain</html></body>"
                        )
            else:
                ads = user_ads
        if ads:
            mos = mos.filter(administrative_domain__in=ads)

        # Working if Administrative domain set
        if ads:
            try:
                match["adm_path"] = {"$in": ads}
                # @todo More 2 level hierarhy
            except bson.errors.InvalidId:
                pass

        addr_map = {mo[0]: (mo[1], mo[2]) for mo in mos.values_list("id", "name", "address")}

        # Active Alarms
        coll = ActiveAlarm._get_collection()
        for aa in coll.aggregate(
            [
                {"$match": match},
                {"$unwind": "$log"},
                {"$match": {"log.source": {"$exists": True, "$ne": None}}},
                {
                    "$project": {
                        "timestamp": 1,
                        "managed_object": 1,
                        "alarm_class": 1,
                        "escalation_tt": 1,
                        "adm_path": 1,
                        "log": 1,
                    }
                },
                {"$sort": {"_id": 1, "log.timestamp": 1}},
            ]
        ):
            r += [
                translate_row(
                    row(
                        [
                            smart_text(aa["_id"]),
                            AlarmClass.get_by_id(aa["alarm_class"]).name,
                            aa["timestamp"],
                            "",
                            aa.get("escalation_tt", ""),
                            addr_map[aa["managed_object"]][0],
                            addr_map[aa["managed_object"]][1],
                            AdministrativeDomain.get_by_id(aa["adm_path"][-1]).name,
                            aa["log"]["timestamp"],
                            aa["log"]["source"],
                            aa["log"]["message"],
                        ]
                    ),
                    cmap,
                )
            ]
        # Active Alarms
        coll = ArchivedAlarm._get_collection()
        for aa in coll.aggregate(
            [
                {"$match": match},
                {"$unwind": "$log"},
                {"$match": {"log.source": {"$exists": True}}},
                {
                    "$project": {
                        "timestamp": 1,
                        "clear_timestamp": 1,
                        "managed_object": 1,
                        "alarm_class": 1,
                        "escalation_tt": 1,
                        "adm_path": 1,
                        "log": 1,
                    }
                },
                {"$sort": {"_id": 1, "log.timestamp": 1}},
            ]
        ):
            r += [
                translate_row(
                    row(
                        [
                            smart_text(aa["_id"]),
                            AlarmClass.get_by_id(aa["alarm_class"]).name,
                            aa["timestamp"],
                            aa["clear_timestamp"],
                            aa.get("escalation_tt", ""),
                            addr_map[aa["managed_object"]][0],
                            addr_map[aa["managed_object"]][1],
                            AdministrativeDomain.get_by_id(aa["adm_path"][-1]).name,
                            aa["log"]["timestamp"],
                            aa["log"]["source"],
                            aa["log"]["message"],
                        ]
                    ),
                    cmap,
                )
            ]
        filename = "alarm_comments.csv"
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="%s"' % filename
            writer = csv.writer(response)
            writer.writerows(r)
            return response
        if o_format == "csv_zip":
            response = BytesIO()
            f = TextIOWrapper(TemporaryFile(mode="w+b"), encoding="utf-8")
            writer = csv.writer(f, dialect="excel", delimiter=";", quotechar='"')
            writer.writerow(columns)
            writer.writerows(r)
            f.seek(0)
            with ZipFile(response, "w", compression=ZIP_DEFLATED) as zf:
                zf.writestr(filename, f.read())
                zf.filename = "%s.zip" % filename
            # response = HttpResponse(content_type="text/csv")
            response.seek(0)
            response = HttpResponse(response.getvalue(), content_type="application/zip")
            response["Content-Disposition"] = 'attachment; filename="%s.zip"' % filename
            return response
        if o_format == "xlsx":
            response = BytesIO()
            wb = xlsxwriter.Workbook(response)
            cf1 = wb.add_format({"bottom": 1, "left": 1, "right": 1, "top": 1})
            ws = wb.add_worksheet("Alarms")
            max_column_data_length = {}
            for rn, x in enumerate(r):
                for cn, c in enumerate(x):
                    if rn and (
                        r[0][cn] not in max_column_data_length
                        or len(str(c)) > max_column_data_length[r[0][cn]]
                    ):
                        max_column_data_length[r[0][cn]] = len(str(c))
                    ws.write(rn, cn, c, cf1)
            ws.autofilter(0, 0, rn, cn)
            ws.freeze_panes(1, 0)
            for cn, c in enumerate(r[0]):
                # Set column width
                width = get_column_width(c)
                if enable_autowidth and width < max_column_data_length[c]:
                    width = max_column_data_length[c]
                ws.set_column(cn, cn, width=width)
            wb.close()
            response.seek(0)
            response = HttpResponse(response.getvalue(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = 'attachment; filename="alarm_comments.xlsx"'
            response.close()
            return response
