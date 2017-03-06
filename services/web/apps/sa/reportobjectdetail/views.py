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
from collections import defaultdict
## Third-party modules
from django.db import connection
from django.http import HttpResponse
from pymongo import ReadPreference
import xlsxwriter
import itertools
import bson
## NOC modules
from noc.lib.nosql import get_db
from noc.lib.app.extapplication import ExtApplication, view
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobject import ManagedObjectAttribute
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.objectstatus import ObjectStatus
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter, IntParameter, BooleanParameter
from noc.sa.models.objectpath import ObjectPath
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.object import Object

# @todo ThreadingCount
# @todo SerialNumber Report
# @todo ReportDiscovery Problem


class ReportObjectLinkCount(object):
    """Report for MO link count"""
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.out = self.load()

    @staticmethod
    def load():
        value = get_db()["noc.links"].aggregate([
            {"$unwind": "$interfaces"},
            {"$lookup": {"from": "noc.interfaces", "localField": "interfaces", "foreignField": "_id", "as": "int"}},
            {"$group": {"_id": "$int.managed_object", "count": {"$sum": 1}}}
        ], read_preference=ReadPreference.SECONDARY_PREFERRED)

        return dict((v["_id"][0], v["count"]) for v in value["result"])

    def __getitem__(self, item):
        return self.out.get(item, 0)


class ReportObjectIfacesTypeStat(object):
    """Report for MO interfaces count"""
    def __init__(self, mo_ids, i_type="physical"):
        self.mo_ids = mo_ids
        self.out = self.load(i_type, self.mo_ids)

    @staticmethod
    def load(i_type, ids):
        match = {"type": i_type}
        if ids:
            match = {"type": i_type,
                     "managed_object": {"$in": ids}}
        value = get_db()["noc.interfaces"].aggregate([
            {"$match": match},
            {"$group": {"_id": "$managed_object", "count": {"$sum": 1}}}
        ], read_preference=ReadPreference.SECONDARY_PREFERRED)

        return dict((v["_id"], v["count"]) for v in value["result"])

    def __getitem__(self, item):
        return self.out.get(item, 0)


class ReportObjectIfacesStatusStat(object):
    """Report for interfaces speed and status count"""
    def __init__(self, mo_ids, columns=list("-")):
        self.mo_ids = mo_ids
        # self.columns = ["1G_UP", "1G_DOWN"]
        self.columns = columns
        self.out = self.load()

    def load(self):
        # @todo Make reports field
        """
        { "_id" : { "managed_object" : 6757 }, "count_in_speed" : 3 }
        { "_id" : { "oper_status" : true, "in_speed" : 10000, "managed_object" : 6757 }, "count_in_speed" : 2 }
        { "_id" : { "oper_status" : true, "in_speed" : 1000000, "managed_object" : 6757 }, "count_in_speed" : 11 }
        { "_id" : { "oper_status" : false, "in_speed" : 1000000, "managed_object" : 6757 }, "count_in_speed" : 62 }
        { "_id" : { "oper_status" : true, "in_speed" : 10000000, "managed_object" : 6757 }, "count_in_speed" : 5 }
        { "_id" : { "oper_status" : false, "in_speed" : 100000, "managed_object" : 6757 }, "count_in_speed" : 1 }
        :return:
        """
        match = {"type": "physical"}
        if self.mo_ids:
            match = {"type": "physical",
                     "managed_object": {"$in": self.mo_ids}}
        value = get_db()["noc.interfaces"].aggregate([
            {"$match": match},
            {"$group": {"_id": {"oper_status": "$oper_status", "in_speed": "$in_speed",
                                "managed_object": "$managed_object"},
                        "count": {"$sum": 1}}}
        ], read_preference=ReadPreference.SECONDARY_PREFERRED)
        def_l = [""] * len(self.columns)
        r = defaultdict(lambda: [""] * len(self.columns))
        for v in value["result"]:
            c = {
                True: "Up",
                False: "Down",
                None: "-"
            }[v["_id"].get("oper_status", None)]

            if v["_id"].get("in_speed", None):
                c += "/" + self.humanize_speed(v["_id"]["in_speed"])
            else:
                c += "/-"
            # r[v["_id"]["managed_object"]].append((c, v["count"]))
            if c in self.columns:
                r[v["_id"]["managed_object"]][self.columns.index(c)] = v["count"]
        return r
        # return dict((v["_id"]["managed_object"], v["count"]) for v in value["result"])

    @staticmethod
    def humanize_speed(speed):
        if not speed:
            return "-"
        for t, n in [
            (1000000, "G"),
            (1000, "M"),
            (1, "k")
        ]:
            if speed >= t:
                if speed // t * t == speed:
                    return "%d%s" % (speed // t, n)
                else:
                    return "%.2f%s" % (float(speed) / t, n)
        return str(speed)

    def __getitem__(self, item):
        return self.out.get(item, ["", "", "", ""])


class ReportObjectAttributes(object):
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.attr_list = ["vendor", "version", "platform"]
        self.out = self.load(self.attr_list)

    @staticmethod
    def load(attr_list):
        """
        :param ids:
        :param attr_list:
        :return: Dict tuple MO attributes mo_id -> (attrs_list)
        :rtype: dict
        """
        mo_attrs = {}
        cursor = connection.cursor()

        base_select = "select %s "
        base_select += "from (select distinct managed_object_id from sa_managedobjectattribute) as saa "

        value_select = "INNER JOIN (select managed_object_id,value from sa_managedobjectattribute where key='%s') "
        value_select += "as %s on %s.managed_object_id=saa.managed_object_id"

        s = ["saa.managed_object_id"]
        s.extend([".".join([al, "value"]) for al in attr_list])

        query1 = base_select % ", ".join(tuple(s))
        query2 = " ".join([value_select % tuple([al]*3) for al in attr_list])
        query = query1 + query2
        cursor.execute(query)
        mo_attrs.update(dict([(c[0], c[1:4]) for c in cursor]))

        return mo_attrs

    def __getitem__(self, item):
        return self.out.get(item, ["", "", ""])


class ReportObjects(object):
    """MO fields report"""
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.out = self.load(mo_ids)
        self.element = None

    @staticmethod
    def load(mos_id):
        query = "select sa.id,sa.name,sa.address, sa.is_managed, "
        query += "profile_name, op.name as object_profile, ad.name as  administrative_domain, sa.segment "
        query += "FROM sa_managedobject sa, sa_managedobjectprofile op, sa_administrativedomain ad "
        query += "WHERE op.id = sa.object_profile_id and ad.id = sa.administrative_domain_id "
        # query += "LIMIT 20"
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor

    def __iter__(self):
        for x in self.out:
            self.element = x[1:]
            yield x[0]

    def __getitem__(self, item):
        # @todo Create dynamic column
        return self.element[item]


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

        type_columns = ["Up/10G", "Up/1G", "Up/100M", "Down/-", "-"]

        cols = [
            "id",
            "object_name",
            "object_address",
            "object_status",
            "profile_name",
            "object_profile",
            "object_vendor",
            "object_platform",
            "object_version",
            "avail",
            "admin_domain",
            "container",
            "segment",
            "phys_interface_count",
            "link_count"
            # "interface_type_count"
        ]

        header_row = [
         "ID",
         "OBJECT_NAME",
         "OBJECT_ADDRESS",
         "OBJECT_STATUS",
         "PROFILE_NAME",
         "OBJECT_PROFILE",
         "OBJECT_VENDOR",
         "OBJECT_PLATFORM",
         "OBJECT_VERSION",
         "AVAIL",
         "ADMIN_DOMAIN",
         "CONTAINER",
         "SEGMENT",
         "PHYS_INTERFACE_COUNT",
         "LINK_COUNT"
         # "INTERFACE_TYPE_COUNT"
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
        if administrative_domain:
            ads = AdministrativeDomain.get_nested_ids(int(administrative_domain))
            mos = mos.filter(administrative_domain__in=ads)
        # discovery = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        mos_id = list(mos.values_list("id", flat=True))
        avail = {}
        segment_lookup = {}
        attr = {}
        moss = []
        iface_count = {}
        link_count = {}
        iface_type_count = {}
        if "segment" in columns.split(","):
            segment_lookup = dict(NetworkSegment.objects.all().values_list("id", "name"))
        if "avail" in columns.split(","):
            avail = ObjectStatus.get_statuses(mos_id)
        if "phys_interface_count" in columns.split(","):
            iface_count = ReportObjectIfacesTypeStat(mos_id)
        if "interface_type_count" in columns.split(","):
            iface_type_count = ReportObjectIfacesStatusStat(mos_id, columns=type_columns)
        if "link_count" in columns.split(","):
            link_count = ReportObjectLinkCount([])
        if len(mos_id) < 70000:
            # @todo Warning - too many objects
            if "object_vendor" in columns.split(",") or "object_platform" in columns.split(",") \
                    or "object_version" in columns.split(","):
                attr = ReportObjectAttributes([])
            moss = ReportObjects([])
        # @todo mo_attributes_lookup
        # @todo segment_name lookup
        for mo in moss:
            if mo not in mos_id:
                continue

            r += [translate_row(row([
                mo,
                moss[0],
                moss[1],
                "managed" if moss[2] else "unmanaged",
                moss[3],
                moss[4],
                attr[mo][0] if attr else "",
                attr[mo][2] if attr else "",
                attr[mo][1] if attr else "",
                _("Yes") if avail.get(mo, None) else _("No"),
                moss[5],
                # mo.container.name if mo.container else "None",
                "None",
                segment_lookup.get(bson.objectid.ObjectId(moss[6]), "No segment") if segment_lookup else "",
                iface_count[mo] if iface_count else "",
                link_count[mo] if link_count else ""
                # iface_type_count[mo] if iface_type_count else ["", "", "", ""]
            ]), cmap)]
            if "interface_type_count" in columns.split(","):
                r[-1].extend(iface_type_count[mo] if iface_type_count else ["", "", "", ""])
            pass

        filename = "mo_detail_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"%s.csv\"" % filename
            writer = csv.writer(response, dialect='excel', delimiter=';')
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
                    "Content-Disposition"] = "attachment; filename=\"%s.xlsx\"" % filename
                with open(f.name) as ff:
                    response.write(ff.read())
                return response
