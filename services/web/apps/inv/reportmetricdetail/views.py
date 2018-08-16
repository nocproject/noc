# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.reportmetricdetail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
import csv
import StringIO
from collections import OrderedDict
# Third-party modules
import xlsxwriter
from django.http import HttpResponse
# NOC modules
from noc.main.models.pool import Pool
from noc.lib.app.extapplication import ExtApplication, view
from noc.lib.app.reportdatasources.report_metrics import (ReportMetrics, ReportCPUMetrics,
                                                          ReportMemoryMetrics, ReportInterfaceFlapMetrics)
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.useraccess import UserAccess


class ReportObjectDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Metric Detail")
    title = _("Object Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    def get_report_object(self, user=None, is_managed=None, adm=None, selector=None,
                          pool=None, segment=None, ids=None):
        p = Pool.get_by_name(pool or "default")
        mos = ManagedObject.objects.filter()
        if user.is_superuser and not adm and not selector and not segment:
            mos = ManagedObject.objects.filter(pool=p)
        if ids:
            mos = ManagedObject.objects.filter(id__in=[ids])
        if is_managed is not None:
            mos = ManagedObject.objects.filter(is_managed=is_managed)
        if pool:
            mos = mos.filter(pool=p)
        if not user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(user))
        if adm:
            ads = AdministrativeDomain.get_nested_ids(int(adm))
            mos = mos.filter(administrative_domain__in=ads)
        if selector:
            selector = ManagedObjectSelector.get_by_id(int(selector))
            mos = mos.filter(selector.Q)
        if segment:
            segment = NetworkSegment.objects.filter(id=segment).first()
            if segment:
                mos = mos.filter(segment__in=segment.get_nested_ids())
        return mos

    @view("^download/$", method=["GET"], access="launch", api=True,
          validate={
              "from_date": StringParameter(required=True),
              "to_date": StringParameter(required=True),
              "administrative_domain": StringParameter(required=False),
              "pool": StringParameter(required=False),
              "segment": StringParameter(required=False),
              "selector": StringParameter(required=False),
              "ids": StringParameter(required=False),
              "detail_stat": StringParameter(required=False),
              "is_managed": BooleanParameter(required=False),
              "avail_status": BooleanParameter(required=False),
              "columns": StringParameter(required=False),
              "o_format": StringParameter(choices=["csv", "xlsx"])})
    def api_report(self, request, o_format, from_date, to_date, is_managed=None,
                   administrative_domain=None, selector=None, pool=None,
                   segment=None, avail_status=False, columns=None, ids=None,
                   detail_stat=None):
        def row(row):
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
            return [qe(x) for x in row]

        def translate_row(row, cmap):
            return [row[i] for i in cmap]
        print columns
        cols = [
            "id",
            "object_name",
            "object_address",
            "iface_name",
            "load_in",
            "load_out",
            "errors_in",
            "errors_out",
            "cpu_usage",
            "memory_usage",
            "interface_flap"
            # "object_hostname",
            # "object_status",
            # "profile_name",
            # "object_profile",
            # "object_vendor",
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

        r = []
        mos = self.get_report_object(request.user, is_managed, administrative_domain,
                                     selector, pool, segment, ids)
        mos_id = tuple(mos.order_by("bi_id").values_list("bi_id", flat=True))
        start = datetime.datetime.strptime(from_date, "%d.%m.%Y")
        stop = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
        # ["load_in", "load_out", "errors_in", "errors_out"]
        a = OrderedDict([(a, "avg(%s)" % a) for a in set(cols[4:]).intersection(set(columns.split(",")))])
        iface_report = ReportMetrics(mos_id, start, stop, columns=a)
        cpu_report = ReportCPUMetrics(mos_id, start, stop)
        memory_report = ReportMemoryMetrics(mos_id, start, stop)
        if "cpu_usage" not in columns.split(","):
            cpu_report = ReportCPUMetrics(mos_id, start, stop).unknown_value
        elif "memory_usage" not in columns.split(","):
            memory_report = ReportMemoryMetrics(mos_id, start, stop).unknown_value
        elif "interface_flap" not in columns.split(","):
            flap_report = ReportInterfaceFlapMetrics(mos_id, start, stop).unknown_value
        # report = iter(report)

        for (mo_id, bi_id, name, address, is_managed,
             sa_profile, o_profile, auth_profile,
             ad, m_segment) in mos.values_list(
                "id", "bi_id", "name", "address", "is_managed",
                "profile", "object_profile__name", "auth_profile__name",
                "administrative_domain__name", "segment").order_by("bi_id"):
            # # o_metrics = next(report)[0]
            c_metrics = next(cpu_report)[0]
            m_metrics = next(memory_report)[0]
            # print cmap
            # print o_metrics
            # for o in o_metrics:
            #     # print o_metrics
            #     k = [
            #         mo_id,
            #         name,
            #         address,
            #         # "managed" if is_managed else "unmanaged",
            #     ] + list(o)
            #     r += [translate_row(row(k), cmap)]

        filename = "mo_metrics_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"%s.csv\"" % filename
            writer = csv.writer(response, dialect='excel', delimiter=';')
            writer.writerows(r)
            return response
        elif o_format == "xlsx":
                response = StringIO.StringIO()
                wb = xlsxwriter.Workbook(response)
                ws = wb.add_worksheet("Objects")
                for rn, x in enumerate(r):
                    for cn, c in enumerate(x):
                        ws.write(rn, cn, c)
                ws.autofilter(0, 0, rn, cn)
                wb.close()
                response.seek(0)
                response = HttpResponse(response.getvalue(),
                                        content_type="application/vnd.ms-excel")
                # response = HttpResponse(
                #     content_type="application/x-ms-excel")
                response[
                    "Content-Disposition"] = "attachment; filename=\"%s.xlsx\"" % filename
                response.close()
                return response
