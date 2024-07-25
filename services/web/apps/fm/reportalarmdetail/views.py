# ---------------------------------------------------------------------
# fm.reportalarmdetail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile
from typing import Optional

# Third-party modules
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
import polars as pl

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter, IntParameter, ObjectIdParameter
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _
from noc.core.comp import smart_bytes
from noc.core.datasources.loader import loader as ds_loader
from noc.core.datasources.base import BaseDataSource


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
    name = name.upper()
    if name.startswith("Up") or name.startswith("Down") or name.startswith("-"):
        return 8
    elif name.startswith("ADM_PATH"):
        return excel_column_format["ADMIN_DOMAIN"]
    elif name in excel_column_format:
        return excel_column_format[name]
    return 15


def get_col_widths(dataframe: "pl.DataFrame", index_filed: Optional[str] = None):
    # First we find the maximum length of the index column
    idx_max = 10
    if index_filed:
        idx_max = max([len(str(s)) for s in dataframe[index_filed]] + [len(str(index_filed))])
    # Then, we concatenate this to the max of the lengths
    # of column name and its values for each column, left to right
    return [idx_max] + [
        max([len(str(s)) for s in dataframe[col]] + [len(col)]) for col in dataframe.columns
    ]


class ReportAlarmDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Alarm Detail")
    title = _("Alarm Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    HEADER_ROW = {
        "root_id": _("ROOT_ID"),
        "from_ts": _("FROM_TS"),
        "to_ts": _("TO_TS"),
        "duration": _("DURATION_SEC"),
        "object_name": _("OBJECT_NAME"),
        "object_address": _("OBJECT_ADDRESS"),
        "object_hostname": _("OBJECT_HOSTNAME"),
        "object_profile": _("OBJECT_PROFILE"),
        "object_object_profile": _("OBJECT_PROFILE"),
        "object_admdomain": _("OBJECT_ADMDOMAIN"),
        "object_platform": _("OBJECT_PLATFORM"),
        "object_version": _("OBJECT_VERSION"),
        "object_project": _("OBJECT_PROJECT"),
        "alarm_class": _("ALARM_CLASS"),
        "alarm_subject": _("ALARM_SUBJECT"),
        "maintenance": _("MAINTENANCE"),
        "objects": _("OBJECTS"),
        "subscribers": _("SUBSCRIBERS"),
        "tt": _("TT"),
        "escalation_ts": _("ESCALATION_TS"),
        "location": _("LOCATION"),
    }

    @view(
        "^download/$",
        method=["GET"],
        access="launch",
        api=True,
        validate={
            "from_date": StringParameter(required=False),
            "to_date": StringParameter(required=False),
            "min_duration": IntParameter(required=False),
            "max_duration": IntParameter(required=False),
            "min_objects": IntParameter(required=False),
            "min_subscribers": IntParameter(required=False),
            "source": StringParameter(
                default="both", choices=["active", "both", "archived", "long_archive"]
            ),
            "segment": ObjectIdParameter(required=False),
            "administrative_domain": IntParameter(required=False),
            "resource_group": ObjectIdParameter(required=False),
            "ex_resource_group": StringParameter(required=False),
            "alarm_class": ObjectIdParameter(required=False),
            "subscribers": StringParameter(required=False),
            "ids": StringParameter(required=False),
            "columns": StringParameter(required=False),
            "o_format": StringParameter(choices=["csv", "csv_zip", "xlsx"]),
        },
    )
    def api_report(
        self,
        request,
        o_format,
        from_date=None,
        to_date=None,
        min_duration=0,
        max_duration=0,
        min_objects=0,
        min_subscribers=0,
        segment=None,
        administrative_domain=None,
        resource_group=None,
        ex_resource_group=None,
        columns=None,
        source="both",
        alarm_class=None,
        subscribers=None,
        ids=None,
        enable_autowidth=False,
    ):
        d_filters = {}
        out_columns = []
        for cc in columns.split(","):
            # if cc == "alarm_id":
            #     # out_columns.append("alarm_id")
            #     continue
            out_columns.append(cc)

        ads = []
        if administrative_domain:
            ads = AdministrativeDomain.get_nested_ids(administrative_domain)

        if not request.user.is_superuser:
            user_ads = UserAccess.get_domains(request.user)
            if administrative_domain and ads:
                if administrative_domain not in user_ads:
                    ads = list(set(ads) & set(user_ads))
                    if not ads:
                        return HttpResponse(
                            "<html><body>Permission denied: Invalid Administrative Domain</html></body>"
                        )
            else:
                ads = user_ads
        if ids:
            ids = ids.split()
            d_filters["objectids"] = ids
            fd = datetime.datetime.now()
            td = None
        elif from_date and to_date:
            fd = datetime.datetime.strptime(from_date, "%d.%m.%Y")
            td = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
        else:
            return HttpResponseBadRequest(_("One params - FROM_DATE/TO_DATE or IDS required"))
        d_filters["start"] = fd
        d_filters["end"] = td
        for name, values in [
            ("min_duration", min_duration),
            ("max_duration", max_duration),
            ("min_objects", min_objects),
            ("min_subscribers", min_subscribers),
            ("segment", segment),
            ("adm_path", ads),
            ("resource_group", resource_group),
            ("ex_resource_group", ex_resource_group),
            ("alarm_class", alarm_class),
            ("subscribers", subscribers),
            ("source", source),
        ]:
            if not values:
                continue
            if values and isinstance(values, list):
                # filters += [{"name": name, "values": values}]
                d_filters[name] = values
            elif values:
                # filters += [{"name": name, "values": [values]}]
                d_filters[name] = [values]
        if source in ["long_archive"]:
            report_ds = "reportdsalarmsbiarchive"
            o_format = "csv_zip"
            if td - fd > datetime.timedelta(days=390):
                return HttpResponseBadRequest(
                    _(
                        "Report more than 1 year not allowed. If nedeed - request it from Administrator"
                    )
                )
            report: "BaseDataSource" = ds_loader[report_ds]
            out_columns = [ff.name for ff in report.fields]
        else:
            report_ds = "reportdsalarms"
            report: "BaseDataSource" = ds_loader[report_ds]
        if not report:
            return HttpResponseNotFound(_(f"Report DataSource {report_ds} Not found"))

        data = report.query_sync(fields=out_columns, **d_filters)
        filename = f'alarms_detail_report_{datetime.datetime.now().strftime("%Y%m%d")}'
        csv_header = ";".join(self.HEADER_ROW.get(cc, cc) for cc in data.columns) + "\n"
        if o_format == "csv":
            response = HttpResponse(
                csv_header
                + data.write_csv(
                    # header=[self.HEADER_ROW.get(cc, cc) for cc in out_columns],
                    separator=";",
                    quote='"',
                    has_header=False,
                ),
                content_type="text/csv",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
            return response
        elif o_format == "csv_zip":
            response = BytesIO()
            f = TemporaryFile(mode="w+b")
            f.write(
                smart_bytes(
                    csv_header
                    + data.select(out_columns).write_csv(
                        # header=[self.HEADER_ROW.get(cc, cc) for cc in out_columns],
                        # columns=out_columns,
                        separator=";",
                        quote='"',
                        has_header=False,
                    )
                )
            )
            f.seek(0)
            with ZipFile(response, "w", compression=ZIP_DEFLATED) as zf:
                zf.writestr(f"{filename}.csv", f.read())
                zf.filename = f"{filename}.zip"
            response.seek(0)
            response = HttpResponse(response.getvalue(), content_type="application/zip")
            response["Content-Disposition"] = f'attachment; filename="{filename}.zip"'
            return response
        elif o_format == "xlsx":
            import xlsxwriter

            response = BytesIO()
            book = xlsxwriter.Workbook(response)
            cf1 = book.add_format({"bottom": 1, "left": 1, "right": 1, "top": 1})
            worksheet = book.add_worksheet("Alarms")
            for cn, col in enumerate(out_columns):
                worksheet.write(0, cn, self.HEADER_ROW.get(col, col), cf1)
            for cn, col in enumerate(out_columns):
                worksheet.write_column(1, cn, data[col], cf1)
            (max_row, max_col) = data.shape
            worksheet.autofilter(0, 0, max_row, len(out_columns))
            worksheet.freeze_panes(1, 0)
            if enable_autowidth:
                for i, width in enumerate(get_col_widths(data)):
                    worksheet.set_column(i, i, width)
            #
            book.close()
            response.seek(0)
            response = HttpResponse(response, content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
            response.close()
            return response
