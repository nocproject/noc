# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportobjectdetail application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import csv
import tempfile
## Third-party modules
from django.http import HttpResponse
import xlsxwriter
import bson
## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.objectstatus import ObjectStatus
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter, IntParameter, BooleanParameter
from noc.sa.models.objectpath import ObjectPath
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.object import Object


class ReportObjectDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Object Detail")
    title = _("Object Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    @view("^download/$", method=["GET"], access="launch", api=True,
          validate={
              "administrative_domain": StringParameter(required=False),
              "segment": StringParameter(required=False),
              "is_managed": BooleanParameter(required=False),
              "avail_status": BooleanParameter(required=False),
              "columns": StringParameter(required=False),
              "format": StringParameter(choices=["csv", "xlsx"])
          })
    def api_report(self, request, format, is_managed=None,
                   administrative_domain=None, avail_status=False,
                   segment=None, columns=None):
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
            r = [qe(x) for x in row]
            return r

        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        cols = [
            "id",
            "object_name",
            "object_address",
            "profile_name",
            "object_profile",
            "object_vendor",
            "object_platform",
            "avail",
            "admin_domain",
            "container",
            "segment"
        ]

        header_row = [
         "ID",
         "OBJECT_NAME",
         "OBJECT_ADDRESS",
         "PROFILE_NAME",
         "OBJECT_PROFILE",
         "OBJECT_VENDOR",
         "OBJECT_PLATFORM",
         "AVAIL",
         "ADMIN_DOMAIN",
         "CONTAINER",
         "SEGMENT"
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

        self.logger.info(r)
        self.logger.info("---------------------------------")
        print("-----------%s------------%s" % (administrative_domain, columns))

        p = Pool.get_by_name("default")
        # for a in ArchivedAlarm._get_collection().find(q).sort(
        mos = ManagedObject.objects.filter()
        if request.user.is_superuser and not administrative_domain:
            mos = ManagedObject.objects.filter(pool=p)
        if is_managed is not None:
            mos = ManagedObject.objects.filter(is_managed=is_managed)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        # if obj_profile:
        #     mos = mos.filter(object_profile=obj_profile)
        if administrative_domain:
            ads = AdministrativeDomain.get_nested_ids(int(administrative_domain))
            mos = mos.filter(administrative_domain__in=ads)
        # discovery = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        avail = {}
        if avail_status:
            mos_id = list(mos.values_list("id", flat=True))
            avail = ObjectStatus.get_statuses(mos_id)

        for mo in mos:
            try:
                s_n = mo.segment.name
            except NetworkSegment.DoesNotExist:
                s_n = "None"
            r += [translate_row(row([
                mo.id,
                mo.name,
                mo.address,
                mo.profile_name,
                mo.object_profile.name,
                mo.vendor,
                mo.platform,
                _("Yes") if avail.get(mo.id, None) else _("No"),
                mo.administrative_domain.name,
                mo.container.name if mo.container else "None",
                s_n
            ]), cmap)]

        if format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"objectss.csv\""
            writer = csv.writer(response)
            writer.writerows(r)
            return response
        elif format == "xlsx":
            with tempfile.NamedTemporaryFile(mode="wb") as f:
                wb = xlsxwriter.Workbook(f.name)
                ws = wb.add_worksheet("Objects")
                for rn, x in enumerate(r):
                    for cn, c in enumerate(x):
                        ws.write(rn, cn, c)
                ws.autofilter(0, 0, rn, cn)
                wb.close()
                response = HttpResponse(
                    content_type="application/x-ms-excel")
                response[
                    "Content-Disposition"] = "attachment; filename=\"objects.xlsx\""
                with open(f.name) as ff:
                    response.write(ff.read())
                return response
