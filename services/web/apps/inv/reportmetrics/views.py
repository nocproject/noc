# ----------------------------------------------------------------------
# inv.reportmetrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import datetime
import time
from collections import namedtuple
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
from noc.lib.app.reportdatasources.report_metrics import (
    ReportInterfaceMetrics,
    ReportCPUMetrics,
    ReportMemoryMetrics,
    ReportPingMetrics,
)
from noc.lib.app.reportdatasources.report_container import ReportContainerData
from noc.sa.models.useraccess import UserAccess
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _
from noc.core.comp import smart_text
from noc.bi.models.mac import MAC as MACDBC


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
    metric_source = {
        "load_interfaces": ReportInterfaceMetrics,
        "load_cpu": ReportCPUMetrics,
        "load_memory": ReportMemoryMetrics,
        "ping": ReportPingMetrics,
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
            "selector": StringParameter(required=False),
            "interface_profile": StringParameter(required=False),
            "exclude_zero": BooleanParameter(required=False),
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
        interface_profile=None,
        selector=None,
        administrative_domain=None,
        columns=None,
        o_format=None,
        enable_autowidth=False,
        **kwargs,
    ):
        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        map_table = {
            "load_interfaces": r"/Interface\s\|\sLoad\s\|\s[In|Out]/",
            "load_cpu": r"/[CPU|Memory]\s\|\sUsage/",
            "errors": r"/Interface\s\|\s[Errors|Discards]\s\|\s[In|Out]/",
            "ping": r"/Ping\s\|\sRTT/",
        }
        cols = [
            "id",
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
            "load_in",
            "load_in_p",
            "load_out",
            "load_out_p",
            "octets_in_sum",
            "octets_out_sum",
            "errors_in",
            "errors_in_sum",
            "errors_out",
            "errors_out_sum",
            "discards_in",
            "discards_in_sum",
            "discards_out",
            "discards_out_sum",
            "lastchange",
            "status_oper",
            "mac_counter",
            "interface_load_url",
            "slot",
            "cpu_usage",
            "memory_usage",
            "ping_rtt",
            "ping_attempts",
            "interface_flap",
        ]

        header_row = [
            "ID",
            "OBJECT_NAME",
            "OBJECT_ADDRESS",
            "OBJECT_PLATFORM",
            "OBJECT_ADM_DOMAIN",
            "OBJECT_SEGMENT",
            "OBJECT_CONTAINER",
            "IFACE_NAME",
            "IFACE_DESCRIPTION",
            "IFACE_SPEED",
            "LOAD_IN (bit/s)",
            "LOAD_IN_P (%)",
            "LOAD_OUT (bit/s)",
            "LOAD_OUT_P (%)",
            "OCTETS_IN_SUM (MB)",
            "OCTETS_OUT_SUM (MB)",
            "ERRORS_IN",
            "ERRORS_IN_SUM",
            "ERRORS_OUT",
            "ERRORS_OUT_SUM",
            "DISCARDS_IN",
            "DISCARDS_IN_SUM",
            "DISCARDS_OUT",
            "DISCARDS_OUT_SUM",
            "INTERFACE_LASTCHANGE",
            "INTERFACE_OPERATION_STATUS",
            "MAC_COUNTER",
            "INTERFACE_LOAD_URL",
            "SLOT",
            "CPU_USAGE",
            "MEMORY_USAGE",
            "PING_RTT",
            "PING_ATTEMPTS",
            "INTERFACE_FLAP",
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
        object_columns = [c for c in columns_order if c.startswith("object")]

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
        if selector:
            mos = mos.filter(ManagedObjectSelector.objects.get(id=int(selector)).Q)
        if administrative_domain:
            mos = mos.filter(
                administrative_domain__in=AdministrativeDomain.get_nested_ids(
                    int(administrative_domain)
                )
            )
        if object_profile:
            mos = mos.filter(object_profile=object_profile)
        # iface_dict = {}

        if "mac_counter" in columns_order:
            macdb = MACDBC()
            ts_cur_date = int(time.time())
            if ts_cur_date - ts_to_date < 0:
                offset = 0
            else:
                offset = round((ts_cur_date - ts_to_date) / 86400)
            mac_aggregate = {}
            for mo in mos:
                mac_responce = macdb.mac_filter(
                    {"managed_object": mo.bi_id}, offset=offset, limit=20000000
                )
                for record in mac_responce:
                    for record in mac_responce:
                        if record["managed_object"] in mac_aggregate.keys():
                            if (
                                record["interface"]
                                in mac_aggregate[record["managed_object"]].keys()
                            ):
                                mac_aggregate[record["managed_object"]][record["interface"]].add(
                                    record["mac"]
                                )
                            else:
                                mac_aggregate[record["managed_object"]].update(
                                    {record["interface"]: {record["mac"]}}
                                )
                        elif mac_aggregate == {}:
                            mac_aggregate = {
                                record["managed_object"]: {record["interface"]: {record["mac"]}}
                            }
                        else:
                            mac_aggregate.update(
                                {record["managed_object"]: {record["interface"]: {record["mac"]}}}
                            )

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

        report_map = {
            "load_interfaces": {
                "url": "%(path)s?title=interface&biid=%(biid)s"
                "&obj=%(oname)s&iface=%(iname)s&from=%(from)s&to=%(to)s",
                "q_group": ["interface"],
                "q_select": {
                    (0, "managed_object", "id"): "managed_object",
                    (1, "path", "iface_name"): "arrayStringConcat(path)",
                },
            },
            "errors": {
                "url": """%(path)s?title=errors&biid=%(biid)s&obj=%(oname)s&iface=%(iname)s&from=%(from)s&to=%(to)s""",
                "q_group": ["interface"],
            },
            "load_cpu": {
                "url": """%(path)s?title=cpu&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
                "q_select": {
                    (0, "managed_object", "id"): "managed_object",
                    (1, "path", "slot"): "arrayStringConcat(path)",
                },
            },
            "ping": {
                "url": """%(path)s?title=ping&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
                "q_select": {(0, "managed_object", "id"): "managed_object"},
            },
        }

        query_map = {
            # "iface_description": ('', 'iface_description', "''"),
            "iface_description": (
                "",
                "iface_description",
                "dictGetString('interfaceattributes','description' , (managed_object, arrayStringConcat(path)))",
            ),
            "iface_speed": (
                "speed",
                "iface_speed",
                "if(max(speed) = 0, dictGetUInt64('interfaceattributes', 'in_speed', "
                "(managed_object, arrayStringConcat(path))), max(speed))",
            ),
            "load_in": ("load_in", "l_in", "round(quantile(0.90)(load_in), 0)"),
            "load_in_p": (
                "load_in",
                "l_in_p",
                "replaceOne(toString(round(quantile(0.90)(load_in) / "
                "if(max(speed) = 0, dictGetUInt64('interfaceattributes', 'in_speed', "
                "(managed_object, arrayStringConcat(path))), max(speed)), 4) * 100), '.', ',')",
            ),
            "load_out": ("load_out", "l_out", "round(quantile(0.90)(load_out), 0)"),
            "load_out_p": (
                "load_out",
                "l_out_p",
                "replaceOne(toString(round(quantile(0.90)(load_out) / "
                "if(max(speed) = 0, dictGetUInt64('interfaceattributes', 'in_speed', "
                "(managed_object, arrayStringConcat(path))), max(speed)), 4) * 100), '.', ',')",
            ),
            "octets_in_sum": (
                "load_in",
                "octets_in_sum",
                "round((sum(load_in * time_delta) / 8) / 1048576)",
            ),
            "octets_out_sum": (
                "load_out",
                "octets_out_sum",
                "round((sum(load_out * time_delta) / 8) / 1048576)",
            ),
            "errors_in": ("errors_in", "err_in", "quantile(0.90)(errors_in)"),
            "errors_in_sum": ("errors_in_delta", "err_in_d", "sum(errors_in_delta)"),
            "errors_out": ("errors_out", "err_out", "quantile(0.90)(errors_out)"),
            "errors_out_sum": ("errors_out_delta", "err_out_d", "sum(errors_out_delta)"),
            "discards_in": ("discards_in", "disc_in", "quantile(0.90)(discards_in)"),
            "discards_in_sum": ("discards_in_delta", "disc_in_d", "sum(discards_in_delta)"),
            "discards_out": ("discards_out", "disc_out", "quantile(0.90)(discards_out)"),
            "discards_out_sum": ("discards_out_delta", "disc_out_d", "sum(discards_out_delta)"),
            "lastchange": ("lastchange", "l_change", "anyLast(lastchange)"),
            "status_oper": ("status_oper", "status_oper", "anyLast(status_oper)"),
            "interface_flap": (
                "interface_flap",
                "flap_count",
                "countEqual(arrayMap((a,p) -> a + p, arrayPushFront(groupArray(status_oper),"
                "groupArray(status_oper)[1]), arrayPushBack(groupArray(status_oper),"
                "groupArray(status_oper)[-1])), 1)",
            ),
            "cpu_usage": ("usage", "cpu_usage", "quantile(0.90)(usage)"),
            "ping_rtt": ("rtt", "ping_rtt", "round(quantile(0.90)(rtt) / 1000, 2)"),
            "ping_attempts": ("attempts", "ping_attempts", "avg(attempts)"),
        }
        query_fields = []
        for c in report_map[reporttype]["q_select"]:
            query_fields += [c[2]]
        field_shift = len(query_fields)  # deny replacing field
        for c in columns.split(","):
            if c not in query_map:
                continue
            field, alias, func = query_map[c]
            report_map[reporttype]["q_select"][
                (columns_order.index(c) + field_shift, field, alias)
            ] = func
            query_fields += [c]
        metrics_attrs = namedtuple("METRICSATTRs", query_fields)

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
                    row[1],
                    row[2],
                    smart_text(Platform.get_by_id(row[3]) if row[3] else ""),
                    row[4],
                    smart_text(NetworkSegment.get_by_id(row[5])) if row[5] else "",
                    containers_address.get(row[6], "") if containers_address and row[6] else "",
                ]
            )
        url = report_map[reporttype].get("url", "")
        report_metric = self.metric_source[reporttype](
            tuple(sorted(moss)), from_date, to_date, columns=None
        )
        report_metric.SELECT_QUERY_MAP = report_map[reporttype]["q_select"]
        if exclude_zero and reporttype == "load_interfaces":
            report_metric.CUSTOM_FILTER["having"] += ["max(load_in) != 0 AND max(load_out) != 0"]
        if interface_profile:
            interface_profile = InterfaceProfile.objects.filter(id=interface_profile).first()
            report_metric.CUSTOM_FILTER["having"] += [
                "dictGetString('interfaceattributes', 'profile', "
                "(managed_object, arrayStringConcat(path))) = '%s'" % interface_profile.name
            ]
        # OBJECT_PLATFORM, ADMIN_DOMAIN, SEGMENT, OBJECT_HOSTNAME
        for row in report_metric.do_query():
            mm = metrics_attrs(*row)
            mo = moss[int(mm.id)]
            res = []
            for y in columns_order:
                if y in object_columns:
                    res += [getattr(mo, y)]
                elif y == "interface_load_url":
                    d_url["biid"] = mm.id
                    d_url["oname"] = mo[2].replace("#", "%23")
                    # res += [url % d_url, interval]$:
                    res.insert(columns_order.index("interface_load_url"), url % d_url)
                elif y == "mac_counter":
                    if getattr(mm, "id") in mac_aggregate.keys():
                        if getattr(mm, "iface_name") in mac_aggregate[getattr(mm, "id")].keys():
                            mac_counter = len(
                                mac_aggregate[getattr(mm, "id")][getattr(mm, "iface_name")]
                            )
                        else:
                            mac_counter = 0
                    else:
                        mac_counter = 0
                    res.insert(columns_order.index("mac_counter"), mac_counter)
                else:
                    res += [getattr(mm, y)]
            r += [res]
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
