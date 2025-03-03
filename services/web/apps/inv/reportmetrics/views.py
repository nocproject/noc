# ----------------------------------------------------------------------
# inv.reportmetrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import datetime
import time
import csv
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile

# Third-party modules
import xlsxwriter
from django.http import HttpResponse

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.platform import Platform
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.resourcegroup import ResourceGroup
from noc.services.web.base.reportdatasources.loader import loader
from noc.services.web.base.reportdatasources.report_container import ReportContainerData
from noc.services.web.base.extapplication import ExtApplication, view
from noc.sa.models.useraccess import UserAccess
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _
from noc.core.comp import smart_text
from noc.core.datasources.loader import loader as ds_loader


def get_column_width(name):
    excel_column_format = {
        "ID": 6,
        "OBJECT_NAME": 38,
        "OBJECT_STATUS": 10,
        "OBJECT_PROFILE": 17,
        "OBJECT_PLATFORM": 25,
        "AVAIL": 6,
        "OBJECT_ADM_DOMAIN": 25,
        "PHYS_INTERFACE_COUNT": 5,
    }
    if name.startswith("Up") or name.startswith("Down") or name.startswith("-"):
        return 8
    elif name.startswith("ADM_PATH"):
        return excel_column_format["ADMIN_DOMAIN"]
    elif name in excel_column_format:
        return excel_column_format[name]
    return 15


class ReportMetricsDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Load Metrics")
    title = _("Load Metrics")
    report_map = {
        "load_interfaces": {
            "url": "%(path)s?title=interface&biid=%(biid)s"
            "&obj=%(oname)s&iface=%(iname)s&from=%(from)s&to=%(to)s",
            "datasource": "reportinterfacemetrics",
            "aggregated_source": "reportinterfacemetricsagg",
        },
        "load_cpu": {
            "url": """%(path)s?title=cpu&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
            "datasource": "reportobjectmetrics",
        },
        "ping": {
            "url": """%(path)s?title=ping&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
            "datasource": "reportavailability",
        },
    }

    @view(
        r"^download/$",
        method=["GET"],
        access="launch",
        api=True,
        validate={
            "from_date": StringParameter(required=True),
            "to_date": StringParameter(required=True),
            "reporttype": StringParameter(
                required=True, choices=["load_interfaces", "load_cpu", "ping"]
            ),
            "administrative_domain": StringParameter(required=False),
            # "pool": StringParameter(required=False),
            "segment": StringParameter(required=False),
            "resource_group": StringParameter(required=False),
            "interface_profile": StringParameter(required=False),
            "exclude_zero": StringParameter(required=False),
            "use_aggregated_source": StringParameter(required=False),
            "filter_default": BooleanParameter(required=False),
            "columns": StringParameter(required=False),
            "o_format": StringParameter(choices=["csv", "csv_zip", "xlsx"]),
        },
    )
    def api_report(
        self,
        request,
        reporttype=None,
        from_date=None,
        to_date=None,
        object_profile=None,
        filter_default=None,
        exclude_zero=None,
        use_aggregated_source=None,
        interface_profile=None,
        resource_group=None,
        administrative_domain=None,
        columns=None,
        o_format=None,
        enable_autowidth=False,
        **kwargs,
    ):

        map_table = {
            "load_interfaces": r"/Interface\s\|\sLoad\s\|\s[In|Out]/",
            "load_cpu": r"/[CPU|Memory]\s\|\sUsage/",
            "errors": r"/Interface\s\|\s[Errors|Discards]\s\|\s[In|Out]/",
            "ping": r"/Ping\s\|\sRTT/",
        }

        # Date Time Block
        if not from_date:
            from_date = datetime.datetime.now() - datetime.timedelta(days=1)
        else:
            from_date = datetime.datetime.strptime(from_date, "%d.%m.%Y")
        if not to_date or from_date == to_date:
            to_date = from_date + datetime.timedelta(days=1)
        else:
            to_date = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
        # interval = (to_date - from_date).days
        ts_from_date = time.mktime(from_date.timetuple())
        ts_to_date = time.mktime(to_date.timetuple())

        # Load managed objects
        mos = ManagedObject.objects.filter(is_managed=True)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if resource_group:
            resource_group = ResourceGroup.get_by_id(resource_group)
            mos = mos.filter(
                effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
            )
        if administrative_domain:
            mos = mos.filter(
                administrative_domain__in=AdministrativeDomain.get_nested_ids(
                    int(administrative_domain)
                )
            )
        if object_profile:
            mos = mos.filter(object_profile=object_profile)

        d_url = {
            "path": "/ui/grafana/dashboard/script/report.js",
            "rname": map_table[reporttype],
            "from": smart_text(int(ts_from_date * 1000)),
            "to": smart_text(int(ts_to_date * 1000)),
            # o.name.replace("#", "%23")
            "biid": "",
            "oname": "",
            "iname": "",
        }

        url = self.report_map[reporttype]["url"]
        columns = columns.split(",")
        containers_address = {}
        if "object_container" in columns:
            containers_address = ReportContainerData(set(mos.values_list("id", flat=True)))
            containers_address = dict(list(containers_address.extract()))

        object_data = {}
        for row in mos.values_list(
            "bi_id", "name", "address", "platform", "administrative_domain__name", "segment", "id"
        ):
            object_data[row[0]] = {
                "object_name": row[1],
                "object_address": row[2],
                "object_platform": Platform.get_by_id(row[3]).full_name if row[3] else "",
                "object_adm_domain": row[4],
                "object_segment": NetworkSegment.get_by_id(row[5]).name if row[5] else "",
                # "object_segment": "",
                "object_container": (
                    containers_address.get(row[6], "") if containers_address and row[6] else ""
                ),
                # "object_container": "",
            }
        datasource = self.report_map[reporttype]["datasource"]
        report = loader[datasource]

        if (
            use_aggregated_source
            and self.report_map[reporttype].get("aggregated_source")
            and loader[self.report_map[reporttype]["aggregated_source"]]
        ):
            agg_map = {"errors_in": "errors_in_avg", "errors_out": "errors_out_avg"}
            columns = [agg_map.get(c, c) for c in columns]
            datasource = "reportinterfacemetricsagg"
            report = loader[datasource]

        fields = ["managed_object"]
        group = ["managed_object"]
        if reporttype == "load_interfaces":
            fields += ["iface_name"]
            group += ["iface_name"]

        header = []
        for c in columns:
            fields += [c]
            for ff in report.FIELDS:
                if ff.name == c:
                    header += [ff.label]
                    break
            else:
                header += [c]
        r = [header]
        columns_filter = set(fields)
        filters = []
        mac_counters = {}
        if "mac_counter" in columns_filter:
            mac_ds = ds_loader["interfacemacsstatds"]
            data = mac_ds.query_sync(resolve_managedobject_id=False, start=from_date, end=to_date)
            mac_counters = {
                (r["managed_object_id"], r["interface_name"]): r["mac_count"]
                for r in data.to_dicts()
            }
        if reporttype == "load_interfaces" and interface_profile:
            interface_profile = InterfaceProfile.objects.filter(id=interface_profile).first()
            filters += [{"name": "interface_profile", "value": [interface_profile.name]}]
        if reporttype == "load_interfaces" and not use_aggregated_source and exclude_zero:
            # Op - operand (function) - default IN
            filters += [
                {"name": "max(load_in)", "value": [0], "op": "!="},
                {"name": "max(load_out)", "value": [0], "op": "!="},
            ]
        elif reporttype == "load_interfaces" and use_aggregated_source and exclude_zero:
            filters += [
                {"name": "maxMerge(load_in_max)", "value": [0], "op": "!="},
                {"name": "maxMerge(load_out_max)", "value": [0], "op": "!="},
            ]

        data = report(
            fields=fields,
            allobjectids=False,
            objectids=list(object_data.keys()),
            start=from_date,
            end=to_date,
            groups=group,
            filters=filters,
        )

        for row in data.extract():
            row.update(object_data[int(row["managed_object"])])
            if "interface_load_url" in columns_filter:
                d_url["biid"] = row["managed_object"]
                d_url["oname"] = row["object_name"]
                row["interface_load_url"] = url % d_url
            if "mac_counter" in columns_filter:
                row["mac_counter"] = mac_counters.get(
                    (int(row["managed_object"]), row["iface_name"]), ""
                )
            res = []
            for y in columns:
                res.append(row.get(y, ""))
            r.append(res)

        filename = "metrics_detail_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="%s.csv"' % filename
            writer = csv.writer(response, dialect="excel", delimiter=",", quoting=csv.QUOTE_MINIMAL)
            writer.writerows(r)
            return response
        elif o_format == "csv_zip":
            response = BytesIO()
            f = TextIOWrapper(TemporaryFile(mode="w+b"), encoding="utf-8")
            writer = csv.writer(f, dialect="excel", delimiter=";", quotechar='"')
            writer.writerows(r)
            f.seek(0)
            with ZipFile(response, "w", compression=ZIP_DEFLATED) as zf:
                zf.writestr("%s.csv" % filename, f.read())
                zf.filename = "%s.csv.zip" % filename
            # response = HttpResponse(content_type="text/csv")
            response.seek(0)
            response = HttpResponse(response.getvalue(), content_type="application/zip")
            response["Content-Disposition"] = 'attachment; filename="%s.csv.zip"' % filename
            return response
        elif o_format == "xlsx":
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
            response["Content-Disposition"] = 'attachment; filename="%s.xlsx"' % filename
            response.close()
            return response
