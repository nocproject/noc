# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.reportmetrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import datetime
import time
from collections import namedtuple
import csv
# Third-party modules
import xlsxwriter
from six import StringIO
from django.http import HttpResponse
# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.platform import Platform
from noc.inv.models.networksegment import NetworkSegment
from noc.lib.app.reportdatasources.report_metrics import ReportInterfaceMetrics, ReportCPUMetrics,\
    ReportMemoryMetrics, ReportPingMetrics
from noc.sa.models.useraccess import UserAccess
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _


def get_column_width(name):
    excel_column_format = {"ID": 6, "OBJECT_NAME": 38, "OBJECT_STATUS": 10, "OBJECT_PROFILE": 17,
                           "OBJECT_PLATFORM": 25, "AVAIL": 6, "OBJECT_ADM_DOMAIN": 25, "PHYS_INTERFACE_COUNT": 5}
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
        "ping": ReportPingMetrics
    }

    @view("^download/$", method=["GET"], access="launch", api=True,
          validate={
              "from_date": StringParameter(required=True),
              "to_date": StringParameter(required=True),
              "reporttype": StringParameter(required=True, choices=["load_interfaces", "load_cpu", "ping"]),
              "administrative_domain": StringParameter(required=False),
              # "pool": StringParameter(required=False),
              "segment": StringParameter(required=False),
              "selector": StringParameter(required=False),
              "interface_profile": StringParameter(required=False),
              "exclude_zero": BooleanParameter(required=False),
              "filter_default": BooleanParameter(required=False),
              "columns": StringParameter(required=False),
              "o_format": StringParameter(choices=["csv", "xlsx"])})
    def api_report(self, request, reporttype=None, from_date=None, to_date=None, object_profile=None,
                   filter_default=None, exclude_zero=None, interface_profile=None, selector=None,
                   administrative_domain=None, columns=None, o_format=None, enable_autowidth=False,
                   **kwargs):

        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        map_table = {"load_interfaces": "/Interface\s\|\sLoad\s\|\s[In|Out]/",
                     "load_cpu": "/[CPU|Memory]\s\|\sUsage/",
                     "errors": "/Interface\s\|\s[Errors|Discards]\s\|\s[In|Out]/",
                     "ping": "/Ping\s\|\sRTT/"}
        cols = [
            "id",
            "object_name",
            "object_address",
            "object_platform",
            "object_adm_domain",
            "object_segment",
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
            "errors_in",
            "errors_out",
            "slot",
            "cpu_usage",
            "memory_usage",
            "ping_rtt",
            "ping_attempts"
            "interface_flap",
            "interface_load_url"
        ]

        header_row = [
            "ID",
            "OBJECT_NAME",
            "OBJECT_ADDRESS",
            "OBJECT_PLATFORM",
            "OBJECT_ADM_DOMAIN",
            "OBJECT_SEGMENT",
            "IFACE_NAME",
            "IFACE_DESCRIPTION",
            "IFACE_SPEED",
            "LOAD_IN",
            "LOAD_IN_P",
            "LOAD_OUT",
            "LOAD_OUT_P",
            "ERRORS_IN",
            "ERRORS_OUT",
            "CPU_USAGE",
            "MEMORY_USAGE",
            "PING_RTT",
            "PING_ATTEMPTS",
            "INTERFACE_FLAP",
            "INTERFACE_LOAD_URL"
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
            mos = mos.filter(
                administrative_domain__in=UserAccess.get_domains(request.user))
        if selector:
            mos = mos.filter(ManagedObjectSelector.objects.get(id=int(selector)).Q)
        if administrative_domain:
            mos = mos.filter(administrative_domain__in=AdministrativeDomain.get_nested_ids(int(administrative_domain)))
        if object_profile:
            mos = mos.filter(object_profile=object_profile)
        iface_dict = {}

        d_url = {
            "path": "/ui/grafana/dashboard/script/report.js",
            "rname": map_table[reporttype],
            "from": str(int(ts_from_date * 1000)),
            "to": str(int(ts_to_date * 1000)),
            # o.name.replace("#", "%23")
            "biid": "",
            "oname": "",
            "iname": ""}

        report_map = {
            "load_interfaces": {
                "url": '%(path)s?title=interface&biid=%(biid)s'
                       '&obj=%(oname)s&iface=%(iname)s&from=%(from)s&to=%(to)s',
                "q_group": ["interface"],
                "q_select": {(0, 'managed_object', None): "managed_object",
                             (1, 'path', 'iface'): "arrayStringConcat(path)"}
            },
            "errors": {
                "url": """%(path)s?title=errors&biid=%(biid)s&obj=%(oname)s&iface=%(iname)s&from=%(from)s&to=%(to)s""",
                "q_group": ["interface"]
            },
            "load_cpu": {
                "url": """%(path)s?title=cpu&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
                "q_select": {(0, 'managed_object', None): "managed_object",
                             (1, 'path', 'slot'): "arrayStringConcat(path)"}
            },
            "ping": {
                "url": """%(path)s?title=ping&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
                "q_select": {(0, 'managed_object', None): "managed_object"}
            }
        }

        query_map = {
            # "iface_description": ('', 'iface_description', "''"),
            "iface_description": (
                '', 'iface_description',
                "dictGetString('interfaceattributes','description' , (managed_object, arrayStringConcat(path)))"),
            "iface_speed": ('speed', 'iface_speed', "max(speed)"),
            "load_in": ('load_in', 'l_in', "round(quantile(0.90)(load_in), 0)"),
            "load_in_p": ('load_in', 'l_in_p',
                          "replaceOne(toString(round(quantile(0.90)(load_in) / "
                          "if(max(speed) = 0, dictGetUInt64('interfaceattributes', 'in_speed', "
                          "(managed_object, arrayStringConcat(path))), max(speed)), 4) * 100), '.', ',')"),
            "load_out": ('load_out', 'l_out', "round(quantile(0.90)(load_out), 0)"),
            "load_out_p": ('load_out', 'l_out_p',
                           "replaceOne(toString(round(quantile(0.90)(load_out) / "
                           "if(max(speed) = 0, dictGetUInt64('interfaceattributes', 'in_speed', "
                           "(managed_object, arrayStringConcat(path))), max(speed)), 4) * 100), '.', ',')"),
            "errors_in": ('errors_in', 'err_in', "quantile(0.90)(errors_in)"),
            "errors_out": ('errors_out', 'err_out', "quantile(0.90)(errors_out)"),
            "cpu_usage": ('usage', 'cpu_usage', "quantile(0.90)(usage)"),
            "ping_rtt": ('rtt', 'ping_rtt', "round(quantile(0.90)(rtt) / 1000, 2)"),
            "ping_attempts": ('attempts', 'ping_attempts', "avg(attempts)")
        }
        for c in columns.split(","):
            if c not in query_map:
                continue
            field, alias, func = query_map[c]
            report_map[reporttype]["q_select"][
                (columns_order.index(c), field, alias)] = func

        mo_attrs = namedtuple("MOATTRs", [c for c in cols if c.startswith("object")])
        moss = {}
        for row in mos.values_list("bi_id", "name", "address", "platform", "administrative_domain__name", "segment"):
            x = mo_attrs(*[row[1], row[2], str(Platform.get_by_id(row[3]) if row[3] else ""),
                           row[4], str(NetworkSegment.get_by_id(row[5])) if row[5] else ""])
            moss[row[0]] = [getattr(x, y) for y in object_columns]
        # if reporttype in ["load_interfaces", "errors"]:
        #     ifaces = Interface._get_collection()
        #     xx = set(mos.values_list("id", flat=True))
        #     for iface in ifaces.find(
        #             {"type": "physical"},
        #             {"managed_object": 1, "name": 1, "description": 1, "in_speed": 1, "out_speed": 1}):
        #         if iface["managed_object"] not in xx:
        #             continue
        #         iface_dict[(iface["managed_object"],
        #                     iface["name"])] = (iface.get("description", ""),
        #                                        iface.get("in_speed", 0), iface.get("out_speed", 0))

        url = report_map[reporttype].get("url", "")
        report_metric = self.metric_source[reporttype](tuple(sorted(moss)), from_date, to_date, columns=None)
        report_metric.SELECT_QUERY_MAP = report_map[reporttype]["q_select"]
        if exclude_zero and reporttype == "load_interfaces":
            report_metric.CUSTOM_FILTER["having"] += ["max(load_in) != 0 AND max(load_out) != 0"]
        if interface_profile:
            interface_profile = InterfaceProfile.objects.filter(id=interface_profile).first()
            report_metric.CUSTOM_FILTER["having"] += [
                "dictGetString('interfaceattributes', 'profile', "
                "(managed_object, arrayStringConcat(path))) = '%s'" % interface_profile.name]
        # OBJECT_PLATFORM, ADMIN_DOMAIN, SEGMENT, OBJECT_HOSTNAM
        for row in report_metric.do_query():
            bi_id, data = row[0], row[1:]
            mo = moss[int(bi_id)]
            res = [bi_id] if "id" in columns_filter else []
            res += mo
            if reporttype == "load_interfaces":
                iface_name, data = data[0], data[1:]
                d_url["iname"] = row[1]
                res += [iface_name]
                res += data
                # if "load_interfaces" in reporttype:
                #     i_d = iface_dict.get((mo[1], l[1]), ["", "", ""])
                #     res.insert(3, i_d[0])
                #     if percent_in:
                #         in_p = float(data[0])
                #         in_p = round((in_p / 1000.0) / (i_d[1] / 100.0), 2) if i_d[1] and in_p > 0 else 0
                #         # in
                #         res.insert(-1, in_p)
                #     if percent_out:
                #         # out
                #         out_p = float(data[1])
                #         res += [round((out_p / 1000.0) / (i_d[2] / 100.0), 2) if i_d[2] and out_p > 0 else 0]
            else:
                res += data
            if "interface_load_url" in columns_filter:
                d_url["biid"] = bi_id
                d_url["oname"] = mo[2].replace("#", "%23")
                # res += [url % d_url, interval]
                res += [url % d_url]
            r += [res]

        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"metrics.csv\""
            writer = csv.writer(response)
            writer.writerows(r)
            return response
        elif o_format == "xlsx":
            response = StringIO()
            wb = xlsxwriter.Workbook(response)
            cf1 = wb.add_format({"bottom": 1, "left": 1, "right": 1, "top": 1})
            ws = wb.add_worksheet("Alarms")
            max_column_data_length = {}
            for rn, x in enumerate(r):
                for cn, c in enumerate(x):
                    if rn and (r[0][cn] not in max_column_data_length or
                               len(str(c)) > max_column_data_length[r[0][cn]]):
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
            response["Content-Disposition"] = "attachment; filename=\"metrics.xlsx\""
            response.close()
            return response
