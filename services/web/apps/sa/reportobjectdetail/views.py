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
import StringIO
from collections import (defaultdict, namedtuple)
# Third-party modules
from django.db import connection
from django.http import HttpResponse
from pymongo import ReadPreference
import xlsxwriter
import bson
# NOC modules
from noc.lib.nosql import (get_db, OperationError)
from noc.lib.app.extapplication import ExtApplication, view
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.inv.models.capability import Capability
from noc.sa.models.authprofile import AuthProfile
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.objectstatus import ObjectStatus
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.profile import Profile
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.vendor import Vendor

# @todo ThreadingCount
# @todo ReportDiscovery Problem

logger = logging.getLogger(__name__)


class ReportObjectBuild(object):

    def __init__(self, site, report, user):
        # Predefined report id
        # <app id>:<variant>
        # "fm.reportavailability:1d"
        self.report = report
        self.site = site
        self.run_as = user

    class RequestStub(object):
        def __init__(self, user):
            self.user = user

    def build_report(self, format_r="raw"):
        """
        Generate report
        :return:
        """
        logger.info("[%s] Building report", self.report)
        app_id, variant = self.report.split(":")
        if app_id not in self.site.apps:
            logger.error("[%s] Invalid application %s. Skipping",
                         self.report, app_id)
            return None
        #
        app = self.site.apps[app_id]
        args = app.get_predefined_args(variant)
        request = self.RequestStub(user=self.run_as)
        report = app.get_data(request, **args)
        if format_r == "csv":
            data = report.to_csv(delimiter=";")
        else:
            data = report
        return data


class ReportAdPath(object):
    """
    Return AD path
    """

    def __init__(self):
        self.out = self.load()

    def load(self):
        cursor = connection.cursor()
        cursor.execute("""SELECT ad.id, ad.name, r.name, ad2.name
                          FROM sa_administrativedomain r
                          JOIN sa_administrativedomain ad ON ad.parent_id = r.id
                          JOIN sa_administrativedomain ad2 ON r.parent_id = ad2.id;
                """)
        return {r[1]: (r[2], r[3]) for r in cursor}

    def __getitem__(self, item):
        return self.out.get(item, [])


class ReportObjectCaps(object):
    """
    Report caps for MO
    Query: db.noc.sa.objectcapabilities.aggregate([{$unwind: "$caps"},
    {$match: {"caps.source" : "caps"}},
    {$project: {key: "$caps.capability", value: "$caps.value"} },
    {$group: {"_id": "$_id", "cap": {$push: { item: "$key", quantity: "$value" } }}}])
    """

    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.caps = dict([("c_%s" % str(key), value) for key, value in
                          Capability.objects.filter().scalar("id", "name")])
        try:
            self.out = self.load(mo_ids)
        except OperationError:
            logger.warning("Operation error when objectcapabilities load")
            self.out = {}

    def load(self, mo_ids):
        # Namedtuple caps, for save
        # @todo
        Caps = namedtuple("Caps", self.caps.keys())
        Caps.__new__.__defaults__ = ("",) * len(Caps._fields)

        i = 0
        d = {}
        while mo_ids[0 + i:10000 + i]:
            match = {"_id": {"$in": mo_ids}}
            value = get_db()["noc.sa.objectcapabilities"].with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate(
                [
                    {"$match": match},
                    {"$unwind": "$caps"},
                    {"$match": {"caps.source": "caps"}},
                    {"$project": {"key": "$caps.capability", "value": "$caps.value"}},
                    {"$group": {"_id": "$_id", "cap": {"$push": {"item": "$key", "val": "$value"}}}}
                ])

            for v in value:
                r = dict(("c_%s" % str(l["item"]), l["val"]) for l in v["cap"] if "c_%s" % str(l["item"]) in self.caps)
                d[v["_id"]] = Caps(**r)
            i += 10000
        return d

    def __getitem__(self, item):
        return self.out.get(item, [""] * len(self.caps))


class ReportObjectDetailLinks(object):
    """Report for MO links detail"""
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.out = self.load(mo_ids)

    @staticmethod
    def load(mo_ids):
        match = {"int.managed_object": {"$in": mo_ids}}
        group = {"_id": "$int.managed_object",
                 "links": {"$push": {"link": "$_id",
                                     "iface_n": "$int.name",
                                     "iface_id": "$int._id",
                                     "mo": "$int.managed_object"}}}
        value = get_db()["noc.links"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$unwind": "$interfaces"},
            {"$lookup": {"from": "noc.interfaces", "localField": "interfaces", "foreignField": "_id", "as": "int"}},
            {"$match": match},
            {"$group": group}
        ])

        return dict((v["_id"][0], v["links"]) for v in value if v["_id"])

    def __getitem__(self, item):
        return self.out.get(item, [])


class ReportDiscoveryResult(object):
    """Report for MO links detail"""
    def __init__(self, mos, avail_only=False, match=None, load=False):
        """

        :param mos:
        :type mos: ManagedObject.objects.filter()
        """
        self.mo_ids = list(mos.values_list("id", flat=True))
        if avail_only:
            status = ObjectStatus.get_statuses(self.mo_ids)
            self.mo_ids = [s for s in status if status[s]]
        self.mos_pools = [Pool.get_by_id(p) for p in set(mos.values_list("pool", flat=True))]
        self.coll_name = "noc.schedules.discovery.%s"
        # @todo Good way for pipelines fill
        self.pipelines = {}
        self.match = match
        self.out = self.load() if load else {}

    def pipeline(self, match=None):
        """
        Generate pipeline for request
        :param match: Match filter
        :type match: dict
        :return:
        :rtype: list
        """
        discovery = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        pipeline = [
            {"$match": {"key": {"$in": self.mo_ids}, "jcls": discovery}},
            {"$project": {
                "j_id": {"$concat": ["discovery-", "$jcls", "-", {"$substr": ["$key", 0, -1]}]},
                "st": True,
                "key": True}},
            {"$lookup": {"from": "noc.joblog", "localField": "j_id", "foreignField": "_id", "as": "job"}},
            {"$project": {"job.problems": True, "st": True, "key": True}}]
        if self.match:
            # @todo check match
            pipeline += [{"$match": self.match}]
        else:
            pipeline += [{"$match": {"job.problems": {"$exists": True, "$ne": {}}}}]
        return pipeline

    def load(self):

        r = defaultdict(dict)
        for v in self.__iter__():
            r[int(v["key"])]["time"] = v["st"]
            r[int(v["key"])]["problems"] = v["job"][0]["problems"]
        # return dict((v["_id"][0], v["count"]) for v in value["result"] if v["_id"])
        return r

    def __iter__(self):
        for p in self.mos_pools:
            r = get_db()[self.coll_name % p.name].with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate(
                self.pipelines.get(p.name, self.pipeline()))
            for x in r:
                # @todo Append info for MO
                yield x

    def __getitem__(self, item):
        return self.out[item] if item in self.out else {"problems": {}, "time": ""}


class ReportContainer(object):
    """Report for MO Container"""
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.out = self.load(self.mo_ids)

    @staticmethod
    def load(mo_ids):
        match = {"data.management.managed_object": {"$exists": True}}
        if mo_ids:
            match = {"data.management.managed_object": {"$in": mo_ids}}
        value = get_db()["noc.objects"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$match": match},
            {"$lookup": {"from": "noc.objects", "localField": "container", "foreignField": "_id", "as": "cont"}},
            {"$project": {"data": 1, "cont.data": 1}}
        ])

        r = defaultdict(dict)
        for v in value:
            if "asset" in v["data"]:
                r[v["data"]["management"]["managed_object"]].update(v["data"]["asset"])
            if v["cont"]:
                if "data" in v["cont"][0]:
                    r[v["data"]["management"]["managed_object"]].update(v["cont"][0]["data"].get("address", {}))
        # return dict((v["_id"][0], v["count"]) for v in value["result"] if v["_id"])
        return r

    def __getitem__(self, item):
        return self.out.get(item, {})


class ReportObjectLinkCount(object):
    """Report for MO link count"""
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.out = self.load()

    @staticmethod
    def load():
        value = get_db()["noc.links"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$unwind": "$interfaces"},
            {"$lookup": {"from": "noc.interfaces", "localField": "interfaces", "foreignField": "_id", "as": "int"}},
            {"$group": {"_id": "$int.managed_object", "count": {"$sum": 1}}}
        ])

        return dict((v["_id"][0], v["count"]) for v in value if v["_id"])

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
        value = get_db()["noc.interfaces"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$match": match},
            {"$group": {"_id": "$managed_object", "count": {"$sum": 1}}}
        ])

        return dict((v["_id"], v["count"]) for v in value)

    def __getitem__(self, item):
        return self.out.get(item, 0)


class ReportObjectIfacesStatusStat(object):
    """Report for interfaces speed and status count"""
    def __init__(self, mo_ids, columns=list("-"), oper=True):
        self.mo_ids = mo_ids
        # self.columns = ["1G_UP", "1G_DOWN"]
        self.columns = columns
        self.oper = oper
        self.out = self.load()

    def load(self):
        # @todo Make reports field
        # @todo Sort Error
        """
        { "_id" : { "managed_object" : 6757 }, "count_in_speed" : 3 }
        { "_id" : { "oper_status" : true, "in_speed" : 10000, "managed_object" : 6757 }, "count_in_speed" : 2 }
        { "_id" : { "oper_status" : true, "in_speed" : 1000000, "managed_object" : 6757 }, "count_in_speed" : 11 }
        { "_id" : { "oper_status" : false, "in_speed" : 1000000, "managed_object" : 6757 }, "count_in_speed" : 62 }
        { "_id" : { "oper_status" : true, "in_speed" : 10000000, "managed_object" : 6757 }, "count_in_speed" : 5 }
        { "_id" : { "oper_status" : false, "in_speed" : 100000, "managed_object" : 6757 }, "count_in_speed" : 1 }
        :return:
        """
        r = defaultdict(lambda: [""] * len(self.columns))
        group = {"in_speed": "$in_speed",
                 "managed_object": "$managed_object"}
        if self.oper:
            group["oper_status"] = "$oper_status"

        match = {"type": "physical"}
        if self.mo_ids:
            match = {"type": "physical",
                     "managed_object": {"$in": self.mo_ids}}
        try:
            value = get_db()["noc.interfaces"].with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED
            ).aggregate([
                {"$match": match},
                {"$group": {"_id": group,
                            "count": {"$sum": 1}}}
            ])
        except OperationError:
            logger.warning("Operation error when interfacestatus load")
            return r
        for v in value:
            c = {
                True: "Up",
                False: "Down",
                None: "-"
            }[v["_id"].get("oper_status", None)] if self.oper else ""

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
        return self.out.get(item, [""] * len(self.columns))


class ReportObjectAttributes(object):
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.attr_list = ["Serial Number", "HW version"]
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

        value_select = "LEFT JOIN (select managed_object_id,value from sa_managedobjectattribute where key='%s') "
        value_select += "as %s on %s.managed_object_id=saa.managed_object_id"

        s = ["saa.managed_object_id"]
        s.extend([".".join([al.replace(" ", "_"), "value"]) for al in attr_list])

        query1 = base_select % ", ".join(tuple(s))
        query2 = " ".join([value_select % tuple([al, al.replace(" ", "_"), al.replace(" ", "_")]) for al in attr_list])
        query = query1 + query2
        cursor.execute(query)
        mo_attrs.update(dict([(c[0], c[1:6]) for c in cursor]))

        return mo_attrs

    def __getitem__(self, item):
        return self.out.get(item, ["", ""])


class ReportAttrResolver(object):
    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.attr_list = ["profile", "vendor", "version", "platform"]
        self.out = self.load(self.attr_list)

    @staticmethod
    def load(attr_list):
        """
        :param ids:
        :param attr_list:
        :return: Dict tuple MO attributes mo_id -> (attrs_list)
        :rtype: dict
        """
        platform = {str(p["_id"]): p["name"] for p in Platform.objects.all().as_pymongo().scalar("id", "name")}
        vendor = {str(p["_id"]): p["name"] for p in Vendor.objects.all().as_pymongo().scalar("id", "name")}
        version = {str(p["_id"]): p["version"] for p in Firmware.objects.all().as_pymongo().scalar("id", "version")}
        profile = {str(p["_id"]): p["name"] for p in Profile.objects.all().as_pymongo().scalar("id", "name")}

        mo_attrs_resolv = {}
        cursor = connection.cursor()

        base_select = "select id, profile, vendor, platform, version from sa_managedobject"

        query1 = base_select

        query = query1
        cursor.execute(query)
        mo_attrs_resolv.update(dict([(c[0], [profile.get(c[1], ""),
                                             vendor.get(c[2], ""),
                                             platform.get(c[3], ""),
                                             version.get(c[4], "")
                                             ])
                                     for c in cursor]))

        return mo_attrs_resolv

    def __getitem__(self, item):
        return self.out.get(item, ["", "", "", ""])


class ReportObjects(object):
    """MO fields report"""
    def __init__(self, mo_ids=()):
        self.mo_ids = mo_ids
        self.out = self.load(mo_ids)
        self.element = None

    @staticmethod
    def load(mos_id):
        query = "select sa.id, sa.name,sa.address, sa.is_managed, sa.auth_profile_id, "
        query += "profile, op.name as object_profile, "
        query += "ad.name as  administrative_domain, sa.segment, array_to_string(sa.tags, ';') "
        query += "FROM sa_managedobject sa, sa_managedobjectprofile op, sa_administrativedomain ad "
        query += "WHERE op.id = sa.object_profile_id and ad.id = sa.administrative_domain_id"
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

    def get_all(self):
        return {e: self.element for e in self}


class ReportObjectsHostname(object):
    """MO hostname"""
    def __init__(self, mo_ids=(), use_facts=False):
        self.mo_ids = mo_ids
        self.out = self.load_discovery(mo_ids)
        if use_facts:
            self.out.update(self.load_facts(mo_ids))
        self.element = None

    @staticmethod
    def load_facts(mos_ids):
        db = get_db()["noc.objectfacts"]
        mos_filter = {"label": "system"}
        if mos_ids:
            mos_filter["object"] = {"$in": mos_ids}
        value = db.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED
                                ).find(mos_filter, {"_id": 0, "object": 1, "attrs.hostname": 1})
        return {v["object"]: v["attrs"].get("hostname") for v in value}

    @staticmethod
    def load_discovery(mos_ids):
        db = get_db()["noc.inv.discovery_id"]
        mos_filter = {}
        if mos_ids:
            mos_filter["object"] = {"$in": mos_ids}
        value = db.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED
                                ).find(mos_filter, {"_id": 0, "object": 1, "hostname": 1})
        return {v["object"]: v.get("hostname") for v in value}

    def __getitem__(self, item):
        # @todo Create dynamic column
        return self.out.get(item)


class ReportObjectDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Object Detail")
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
            "id",
            "object_name",
            "object_address",
            "object_status",
            "profile_name",
            "object_profile",
            "object_vendor",
            "object_platform",
            "object_version",
            "object_serial",
            "auth_profile",
            "avail",
            "admin_domain",
            "container",
            "segment",
            "phys_interface_count",
            "link_count",
            # "adm_path"
            # "discovery_problem"
            # "object_tags"
            # "sorted_tags"
            # "object_caps"
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
            "OBJECT_SERIAL",
            "AUTH_PROFILE",
            "AVAIL",
            "ADMIN_DOMAIN",
            "CONTAINER",
            "SEGMENT",
            "PHYS_INTERFACE_COUNT",
            "LINK_COUNT",
        ]
        # "ADM_PATH
        # "DISCOVERY_PROBLEM"
        # "OBJECT_TAGS"
        # "SORTED_TAGS"
        # "OBJECT_CAPS"
        # "INTERFACE_TYPE_COUNT"

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
        if len(mos_id) > 70000:
            return self.response("Request Too Large, Objects limit is 70000", status=self.TOO_LARGE)
        avail = {}
        segment_lookup = {}
        attr = {}
        attr_resolv = {}
        moss = []
        iface_count = {}
        link_count = {}
        discovery_problem = {}
        iface_type_count = {}
        object_caps = {}
        tags_o = []
        container_lookup = ReportContainer(mos_id)
        auth_resolve = dict(AuthProfile.objects.filter().values_list("id", "name"))
        if "adm_path" in columns.split(","):
            ad_path = ReportAdPath()
            r[-1].extend([_("ADM_PATH1"), _("ADM_PATH1"), _("ADM_PATH1")])
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
        if "object_caps" in columns.split(","):
            object_caps = ReportObjectCaps(mos_id)
            caps_columns = object_caps.caps.values()
            r[-1].extend(caps_columns)
        if "object_tags" in columns.split(","):
            r[-1].extend([_("OBJECT_TAGS")])
        if "sorted_tags" in columns.split(","):
            tags = set()
            for s in ManagedObject.objects.filter(is_managed=True).exclude(
                    tags=None).values_list('tags', flat=True).distinct():
                tags.update(set(s))
            tags_o = sorted([t for t in tags if "{" not in t])
            r[-1].extend(tags_o)
        if "discovery_problem" in columns.split(","):
            discovery_problem = ReportDiscoveryResult(mos, load=True)
            # print(discovery_problem.out)
            discovery = ["suggest_snmp", "suggest_cli", "profile",
                         "version", "caps", "interface", "chassis_id"]
            r[-1].extend(discovery)

        if len(mos_id) < 70000:
            # @todo Warning - too many objects
            if "object_serial" in columns.split(","):
                attr = ReportObjectAttributes([])
            attr_resolv = ReportAttrResolver([])
            moss = ReportObjects([])
        # @todo segment_name lookup
        for mo in moss:
            if mo not in mos_id:
                continue
            r += [translate_row(row([
                mo,
                moss[0],
                moss[1],
                "managed" if moss[2] else "unmanaged",
                attr_resolv[mo][0],
                # Profile
                moss[5],
                attr_resolv[mo][1] if attr_resolv else "",
                attr_resolv[mo][2] if attr_resolv else "",
                attr_resolv[mo][3] if attr_resolv else "",
                # Serial
                attr[mo][0] if attr and len(attr[mo]) > 3 else container_lookup[mo].get("serial", ""),
                auth_resolve.get(moss[3], ""),  # Auth profile
                _("Yes") if avail.get(mo, None) else _("No"),
                moss[6],
                container_lookup[mo].get("text", ""),
                segment_lookup.get(bson.objectid.ObjectId(moss[7]), "No segment") if segment_lookup else "",
                iface_count[mo] if iface_count else "",
                link_count[mo] if link_count else "",
                # iface_type_count[mo] if iface_type_count else ["", "", "", ""]
            ]), cmap)]
            if "adm_path" in columns.split(","):
                r[-1].extend([moss[6]] + list(ad_path[moss[6]]))
            if "interface_type_count" in columns.split(","):
                r[-1].extend(iface_type_count[mo] if iface_type_count else ["", "", "", ""])
            if "object_caps" in columns.split(","):
                r[-1].extend(object_caps[mo][:])
            if "object_tags" in columns.split(","):
                r[-1].extend([moss[8]] if moss[8] else [])
            if "sorted_tags" in columns.split(","):
                out_tags = [""] * len(tags_o)
                if moss[8]:
                    for m in moss[8].split(";"):
                        out_tags[tags_o.index(m)] = m
                r[-1].extend(out_tags)
                # r[-1].extend(sorted(moss[7].split(";") if moss[7] else []))
            if "discovery_problem" in columns.split(","):
                dp = discovery_problem[mo] if discovery_problem else {"problems": {}}
                r[-1].extend([dp["problems"].get(d, {"": ""})[""] for d in discovery])

        filename = "mo_detail_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"%s.csv\"" % filename
            writer = csv.writer(response, dialect='excel', delimiter=';')
            writer.writerows(r)
            return response
        elif o_format == "xlsx":
            # with tempfile.NamedTemporaryFile(mode="wb") as f:

            #    wb = xlsxwriter.Workbook(f.name)
                response = StringIO.StringIO()
                wb = xlsxwriter.Workbook(response)
                ws = wb.add_worksheet("Objects")
                for rn, x in enumerate(r):
                    for cn, c in enumerate(x):
                        ws.write(rn, cn, c)
                ws.autofilter(0, 0, rn, cn)
                wb.close()
                response.seek(0)
                response = HttpResponse(response.getvalue(), content_type="application/vnd.ms-excel")

                # response = HttpResponse(
                #     content_type="application/x-ms-excel")
                response[
                    "Content-Disposition"] = "attachment; filename=\"%s.xlsx\"" % filename
                response.close()
                return response
