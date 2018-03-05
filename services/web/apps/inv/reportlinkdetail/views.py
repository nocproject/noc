# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.reportobjectdetail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
import csv
import tempfile
# Third-party modules
from django.http import HttpResponse
from pymongo import ReadPreference
import xlsxwriter
# NOC modules
from noc.lib.nosql import get_db
from noc.lib.app.extapplication import ExtApplication, view
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.inv.models.networksegment import NetworkSegment
from noc.services.web.apps.sa.reportobjectdetail.views import ReportObjects

logger = logging.getLogger(__name__)


class ReportLinksDetail(object):
    """Report for MO links detail"""
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.out = self.load(mo_ids)

    @staticmethod
    def load(mo_ids):
        # match = {"links.mo": {"$in": mo_ids}}
        match = {"int.managed_object": {"$in": mo_ids}}
        group = {"_id": "$_id",
                 "links": {"$push": {"iface_n": "$int.name",
                                     "iface_id": "$int._id",
                                     "dis_method": "$discovery_method",
                                     "last_seen": "$last_seen",
                                     "mo": "$int.managed_object"}}}
        value = get_db()["noc.links"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$unwind": "$interfaces"},
            {"$lookup": {"from": "noc.interfaces", "localField": "interfaces", "foreignField": "_id", "as": "int"}},
            {"$match": match},
            {"$group": group}
        ])

        return dict((v["_id"], v["links"]) for v in value if v["_id"])

    def __getitem__(self, item):
        return self.out.get(item, [])


class ReportLinkDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Link Detail")
    title = _("Object Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    @view("^download/$", method=["GET"], access="launch", api=True,
          validate={
              "administrative_domain": StringParameter(required=False),
              "pool": StringParameter(required=False),
              "segment": StringParameter(required=False),
              "selector": StringParameter(required=False),
              "ids": StringParameter(required=False),
              "is_managed": BooleanParameter(required=False),
              "avail_status": BooleanParameter(required=False),
              "columns": StringParameter(required=False),
              "o_format": StringParameter(choices=["csv", "xlsx"])})
    def api_report(self, request, o_format, is_managed=None,
                   administrative_domain=None, selector=None, pool=None,
                   segment=None, avail_status=False, columns=None, ids=None):
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

        type_columns = ["Up/10G", "Up/1G", "Up/100M", "Down/-", "-"]

        cols = [
            "admin_domain",
            # "id",
            "object1_name",
            "object1_address",
            "object1_iface",
            "object2_name",
            "object2_address",
            "object2_iface",
            "link_proto",
            "last_seen"
        ]

        header_row = [
            "ADMIN_DOMAIN",
            "OBJECT1_NAME",
            "OBJECT1_ADDRESS",
            "OBJECT1_IFACE",
            "OBJECT2_NAME",
            "OBJECT2_ADDRESS",
            "OBJECT2_IFACE",
            "LINK_PROTO",
            "LAST_SEEN"
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
        if "interface_type_count" in columns.split(","):
            r[-1].extend(type_columns)

        # self.logger.info(r)
        # self.logger.info("---------------------------------")
        # print("-----------%s------------%s" % (administrative_domain, columns))

        p = Pool.get_by_name(pool or "default")
        mos = ManagedObject.objects.filter()
        if request.user.is_superuser and not administrative_domain and not selector and not segment:
            mos = ManagedObject.objects.filter(pool=p)
        if ids:
            mos = ManagedObject.objects.filter(id__in=[ids])
        if is_managed is not None:
            mos = ManagedObject.objects.filter(is_managed=is_managed)
        if pool:
            mos = mos.filter(pool=p)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if administrative_domain:
            ads = AdministrativeDomain.get_nested_ids(int(administrative_domain))
            mos = mos.filter(administrative_domain__in=ads)
        if selector:
            selector = ManagedObjectSelector.get_by_id(int(selector))
            mos = mos.filter(selector.Q)
        if segment:
            segment = NetworkSegment.objects.filter(id=segment).first()
            if segment:
                mos = mos.filter(segment__in=segment.get_nested_ids())
        mos_id = list(mos.values_list("id", flat=True))

        rld = ReportLinksDetail(mos_id)

        ro = ReportObjects()
        mo_resolv = ro.get_all()

        for link in rld.out:
            s1, s2 = rld.out[link]
            r += [translate_row(row([
                mo_resolv[s1["mo"][0]][5],
                mo_resolv[s1["mo"][0]][0],
                mo_resolv[s1["mo"][0]][1],
                s1["iface_n"][0],
                mo_resolv[s2["mo"][0]][0],
                mo_resolv[s2["mo"][0]][1],
                s2["iface_n"][0],
                s1.get("dis_method", ""),
                s1.get("last_seen", "")
            ]), cmap)]

        filename = "links_detail_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"%s.csv\"" % filename
            writer = csv.writer(response, dialect='excel', delimiter=';')
            writer.writerows(r)
            return response
        elif o_format == "xlsx":
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
                    "Content-Disposition"] = "attachment; filename=\"%s.xlsx\"" % filename
                with open(f.name) as ff:
                    response.write(ff.read())
                return response
