# ----------------------------------------------------------------------
# inv.reportmaxmetrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict
from collections import namedtuple
import csv
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile

# Third-party modules
import xlsxwriter
from django.http import HttpResponse
from pymongo import ReadPreference

# NOC modules
from noc.inv.models.platform import Platform
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.services.web.base.reportdatasources.report_metrics import ReportInterfaceMetrics
from noc.sa.models.managedobject import ManagedObject
from noc.services.web.base.reportdatasources.report_container import ReportContainerData
from noc.sa.models.useraccess import UserAccess
from noc.services.web.base.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.core.comp import smart_text
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.mongo.connection import get_db
from noc.core.translation import ugettext as _
from noc.config import config


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


class ReportMaxMetricsmaxDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Load Metrics max")
    title = _("Load Metrics max")

    @view(
        r"^download/$",
        method=["GET"],
        access="launch",
        api=True,
        validate={
            "from_date": StringParameter(required=True),
            "to_date": StringParameter(required=True),
            "administrative_domain": StringParameter(required=False),
            # "pool": StringParameter(required=False),
            "segment": StringParameter(required=False),
            "resource_group": StringParameter(required=False),
            "object_profile": StringParameter(required=False),
            "interface_profile": StringParameter(required=False),
            "exclude_zero": BooleanParameter(required=False),
            "filter_default": BooleanParameter(required=False),
            "columns": StringParameter(required=False),
            "description": StringParameter(required=False),
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
        exclude_zero=True,
        interface_profile=None,
        resource_group=None,
        administrative_domain=None,
        columns=None,
        description=None,
        o_format=None,
        enable_autowidth=False,
        **kwargs,
    ):
        def load(mo_ids):
            # match = {"links.mo": {"$in": mo_ids}}
            match = {"int.managed_object": {"$in": mo_ids}}
            group = {
                "_id": "$_id",
                "links": {
                    "$push": {
                        "iface_n": "$int.name",
                        # "iface_id": "$int._id",
                        # "iface_descr": "$int.description",
                        # "iface_speed": "$int.in_speed",
                        # "dis_method": "$discovery_method",
                        # "last_seen": "$last_seen",
                        "mo": "$int.managed_object",
                        "linked_obj": "$linked_objects",
                    }
                },
            }
            value = (
                get_db()["noc.links"]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(
                    [
                        {"$unwind": "$interfaces"},
                        {
                            "$lookup": {
                                "from": "noc.interfaces",
                                "localField": "interfaces",
                                "foreignField": "_id",
                                "as": "int",
                            }
                        },
                        {"$match": match},
                        {"$group": group},
                    ],
                    allowDiskUse=True,
                )
            )

            res = defaultdict(dict)

            for v in value:
                if v["_id"]:
                    for vv in v["links"]:
                        if len(vv["linked_obj"]) == 2:
                            mo = vv["mo"][0]
                            iface = vv["iface_n"]
                            for i in vv["linked_obj"]:
                                if mo != i:
                                    res[mo][i] = iface[0]
            return res

        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        def str_to_float(str):
            return float("{0:.3f}".format(float(str)))

        cols = [
            "object_id",
            "object_name",
            "object_address",
            "object_platform",
            "object_adm_domain",
            "object_segment",
            "object_container",
            # "object_hostname",
            # "object_status",
            # "profile_name",
            # "object_profile",
            # "object_vendor",
            "iface_name",
            "iface_description",
            "iface_speed",
            "max_load_in",
            "max_load_in_time",
            "max_load_out",
            "max_load_out_time",
            "avg_load_in",
            "avg_load_out",
            "total_in",
            "total_out",
            "uplink_iface_name",
            "uplink_iface_description",
            "uplink_iface_speed",
            "uplink_max_load_in",
            "uplink_max_load_in_time",
            "uplink_max_load_out",
            "uplink_max_load_out_time",
            "uplink_avg_load_in",
            "uplink_avg_load_out",
            "uplink_total_in",
            "uplink_total_out",
        ]

        header_row = [
            "ID",
            _("OBJECT_NAME"),
            _("OBJECT_ADDRESS"),
            _("OBJECT_PLATFORM"),
            _("OBJECT_ADMDOMAIN"),
            _("OBJECT_SEGMENT"),
            _("CONTAINER_ADDRESS"),
            _("IFACE_NAME"),
            _("IFACE_DESCRIPTION"),
            _("IFACE_SPEED"),
            _("MAX_LOAD_IN, Mbps"),
            _("MAX_LOAD_IN_TIME"),
            _("MAX_LOAD_OUT, Mbps"),
            _("MAX_LOAD_OUT_TIME"),
            _("AVG_LOAD_IN, Mbps"),
            _("AVG_LOAD_OUT, Mbps"),
            _("TOTAL_IN, Mbyte"),
            _("TOTAL_OUT, Mbyte"),
            _("UPLINK_IFACE_NAME"),
            _("UPLINK_IFACE_DESCRIPTION"),
            _("UPLINK_IFACE_SPEED"),
            _("UPLINK_MAX_LOAD_IN, Mbps"),
            _("UPLINK_MAX_TIME_IN"),
            _("UPLINK_MAX_LOAD_OUT, Mbps"),
            _("UPLINK_MAX_TIME_OUT"),
            _("UPLINK_AVG_LOAD_IN, Mbps"),
            _("UPLINK_AVG_LOAD_OUT, Mbps"),
            _("UPLINK_TOTAL_IN, Mbyte"),
            _("UPLINK_TOTAL_OUT, Mbyte"),
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
        columns_order = columns.split(",")
        columns_filter = set(columns_order)
        r = [translate_row(header_row, cmap)]

        # Date Time Block
        if not from_date:
            from_date = datetime.datetime.now() - datetime.timedelta(days=1)
        else:
            from_date = datetime.datetime.strptime(from_date, "%d.%m.%Y")
        if not to_date or from_date == to_date:
            to_date = from_date + datetime.timedelta(days=1)
        else:
            to_date = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
        diff = to_date - from_date

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
        if interface_profile:
            interface_profile = InterfaceProfile.objects.filter(id=interface_profile).first()

        mo_attrs = namedtuple("MOATTRs", [c for c in cols if c.startswith("object")])

        containers_address = {}
        if "object_container" in columns_filter:
            containers_address = ReportContainerData(set(mos.values_list("id", flat=True)))
            containers_address = dict(list(containers_address.extract()))

        moss = {}
        for row in mos.values_list(
            "bi_id", "name", "address", "platform", "administrative_domain__name", "segment", "id"
        ):
            moss[row[0]] = mo_attrs(
                *[
                    row[6],
                    row[1],
                    row[2],
                    smart_text(Platform.get_by_id(row[3]) if row[3] else ""),
                    row[4],
                    smart_text(NetworkSegment.get_by_id(row[5])) if row[5] else "",
                    containers_address.get(row[6], "") if containers_address and row[6] else "",
                ]
            )

        report_metric = ReportInterfaceMetrics(
            tuple(sorted(moss)), from_date, to_date, columns=None
        )
        report_metric.SELECT_QUERY_MAP = {
            (0, "managed_object", "id"): "managed_object",
            (1, "path", "iface_name"): "arrayStringConcat(path)",
            (
                2,
                "",
                "iface_description",
            ): f"dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes','description' , (managed_object, arrayStringConcat(path)))",
            (
                3,
                "",
                "profile",
            ): f"dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', 'profile', (managed_object, arrayStringConcat(path)))",
            (
                4,
                "speed",
                "iface_speed",
            ): f"dictGetUInt64('{config.clickhouse.db_dictionaries}.interfaceattributes', 'in_speed', (managed_object, arrayStringConcat(path)))",
            (5, "load_in_max", "load_in_max"): "divide(max(load_in),1048576)",
            (6, "load_out_max", "load_out_max"): "divide(max(load_out),1048576)",
            (7, "max_load_in_time", "max_load_in_time"): "argMax(ts,load_in)",
            (8, "max_load_out_time", "max_load_out_time"): "argMax(ts,load_out)",
            (9, "avg_load_in", "avg_load_in"): "divide(avg(load_in),1048576)",
            (10, "avg_load_out", "avg_load_out"): "divide(avg(load_out),1048576)",
        }
        report_metric.CUSTOM_FILTER["having"] = [
            "isNotNull(load_in_max)",
            "isNotNull(load_out_max)",
        ]
        ifaces_metrics = defaultdict(dict)

        for row in report_metric.do_query():
            avg_in = str_to_float(row[9])
            avg_out = str_to_float(row[10])
            total_in = avg_in * diff.total_seconds() / 8
            total_out = avg_out * diff.total_seconds() / 8
            ifaces_metrics[row[0]][row[1]] = {
                "description": row[2],
                "profile": row[3],
                "bandwidth": row[4],
                "max_load_in": str_to_float(row[5]),
                "max_load_out": str_to_float(row[6]),
                "max_load_in_time": row[7],
                "max_load_out_time": row[8],
                "avg_load_in": avg_in,
                "avg_load_out": avg_out,
                "total_in": float("{0:.1f}".format(total_in)),
                "total_out": float("{0:.1f}".format(total_out)),
            }

        # find uplinks
        links = {}
        if cmap[-1] > 17:
            mos_id = list(mos.values_list("id", flat=True))
            uplinks = {obj: [] for obj in mos_id}
            for mo_id, mo_uplinks in mos.values_list("id", "uplinks"):
                uplinks[mo_id] = mo_uplinks or []
            rld = load(mos_id)

            for mo in uplinks:
                for uplink in uplinks[mo]:
                    if rld[mo]:
                        if mo in links:
                            links[mo] += [rld[mo][uplink]]
                        else:
                            links[mo] = [rld[mo][uplink]]

        for mo_bi in ifaces_metrics:
            mo_id = moss[int(mo_bi)]
            mo_ids = getattr(mo_id, "object_id")

            for i in ifaces_metrics[mo_bi]:
                if not exclude_zero:
                    if (
                        ifaces_metrics[mo_bi][i]["max_load_in"] == 0
                        and ifaces_metrics[mo_bi][i]["max_load_out"] == 0
                    ):
                        continue
                if description:
                    if description not in ifaces_metrics[mo_bi][i]["description"]:
                        continue
                if interface_profile:
                    if interface_profile.name not in ifaces_metrics[mo_bi][i]["profile"]:
                        continue

                row2 = [
                    mo_ids,
                    getattr(mo_id, "object_name"),
                    getattr(mo_id, "object_address"),
                    getattr(mo_id, "object_platform"),
                    getattr(mo_id, "object_adm_domain"),
                    getattr(mo_id, "object_segment"),
                    getattr(mo_id, "object_container"),
                    i,
                    ifaces_metrics[mo_bi][i]["description"],
                    ifaces_metrics[mo_bi][i]["bandwidth"],
                    ifaces_metrics[mo_bi][i]["max_load_in"],
                    ifaces_metrics[mo_bi][i]["max_load_in_time"],
                    ifaces_metrics[mo_bi][i]["max_load_out"],
                    ifaces_metrics[mo_bi][i]["max_load_out_time"],
                    ifaces_metrics[mo_bi][i]["avg_load_in"],
                    ifaces_metrics[mo_bi][i]["avg_load_out"],
                    ifaces_metrics[mo_bi][i]["total_in"],
                    ifaces_metrics[mo_bi][i]["total_out"],
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]

                ss = True
                if mo_ids in links:
                    for ifname_uplink in links[mo_ids]:
                        if ifname_uplink in ifaces_metrics[mo_bi]:
                            row2[18] = ifname_uplink
                            row2[19] = ifaces_metrics[mo_bi][ifname_uplink]["description"]
                            row2[20] = ifaces_metrics[mo_bi][ifname_uplink]["bandwidth"]
                            row2[21] = ifaces_metrics[mo_bi][ifname_uplink]["max_load_in"]
                            row2[22] = ifaces_metrics[mo_bi][ifname_uplink]["max_load_in_time"]
                            row2[23] = ifaces_metrics[mo_bi][ifname_uplink]["max_load_out"]
                            row2[24] = ifaces_metrics[mo_bi][ifname_uplink]["max_load_out_time"]
                            row2[25] = ifaces_metrics[mo_bi][ifname_uplink]["avg_load_in"]
                            row2[26] = ifaces_metrics[mo_bi][ifname_uplink]["avg_load_out"]
                            row2[27] = ifaces_metrics[mo_bi][ifname_uplink]["total_in"]
                            row2[28] = ifaces_metrics[mo_bi][ifname_uplink]["total_out"]
                            r += [translate_row(row2, cmap)]
                            ss = False
                if ss:
                    r += [translate_row(row2, cmap)]

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
            ws = wb.add_worksheet("Metrics")
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
