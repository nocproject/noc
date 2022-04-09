# ---------------------------------------------------------------------
# fm.reportalarmdetail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from io import BytesIO
from functools import partial
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile

# Third-party modules
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter, IntParameter, ObjectIdParameter
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _
from noc.lib.app.reportdatasources.base import ReportDataSource
from noc.lib.app.reportdatasources.loader import loader
from noc.core.comp import smart_bytes
from noc.core.ioloop.util import run_sync
from noc.core.datasources.loader import loader as ds_loader


class ReportDsAlarms(object):
    def __init__(self, filters=None):
        self.datasource = ds_loader["reportdsalarms"]
        self.result = None
        self.filters = filters or {}

    def run(self, start, end):
        self.filters["start"] = start
        self.filters["end"] = end
        self.result = run_sync(partial(self.datasource.query, **self.filters))

    def report_csv(self):
        return self.result.to_csv()

    def report_xlsx(self):
        response = BytesIO()
        self.result.to_excel(response)
        response.seek(0)
        return response.getvalue()


class ReportAlarmDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Alarm Detail")
    title = _("Alarm Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

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
                default="both", choices=["active", "both", "archive", "long_archive"]
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
        filters = []
        d_filters = {}

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
        elif from_date:
            fd = datetime.datetime.strptime(from_date, "%d.%m.%Y")
            td = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
        else:
            return HttpResponseBadRequest(_("One param - FROM_DATE or IDS required"))
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
                filters += [{"name": name, "values": values}]
                d_filters[name] = values
            elif values:
                filters += [{"name": name, "values": [values]}]
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
        else:
            report_ds = "reportdsalarms"
        report: ReportDataSource = loader[report_ds]
        if not report:
            return HttpResponseNotFound(_(f"Report DataSource {report_ds} Not found"))
        # data = report(
        #     fields=columns.split(","),
        #     objectids=ids or [],
        #     allobjectids=False,
        #     start=fd,
        #     end=td,
        #     filters=filters,
        # )
        # report = ReportDsAlars(d_filters)
        data = ReportDsAlarms(d_filters)
        data.run(start=fd, end=td)

        filename = f'alarm_detail_report_{datetime.datetime.now().strftime("%Y%m%d")}'
        if o_format == "csv":
            response = HttpResponse(data.report_csv(), content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="%s"' % filename
            return response
        elif o_format == "csv_zip":
            response = BytesIO()
            f = TemporaryFile(mode="w+b")
            f.write(smart_bytes(data.report_csv()))
            f.seek(0)
            with ZipFile(response, "w", compression=ZIP_DEFLATED) as zf:
                zf.writestr(filename, f.read())
                zf.filename = "%s.zip" % filename
            response.seek(0)
            response = HttpResponse(response.getvalue(), content_type="application/zip")
            response["Content-Disposition"] = 'attachment; filename="%s.zip"' % filename
            return response
        elif o_format == "xlsx":
            response = HttpResponse(data.report_xlsx(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = 'attachment; filename="alarms.xlsx"'
            response.close()
            return response
