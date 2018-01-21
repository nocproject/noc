# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ReportDictionary implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
from collections import (defaultdict, namedtuple)
# Third-party modules
from django.db import connection
from pymongo import ReadPreference
import bson
# NOC modules
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.capability import Capability
from noc.sa.models.objectstatus import ObjectStatus
from noc.sa.models.profile import Profile
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.vendor import Vendor


class ReportDictionary(object):
    """
    Report Dictionary
    Return dict {id: value} there fill method load(), else unknown method
    Optional Attribute return list Value Name
    """
    UNKNOWN = []
    ATTRS = []

    logger = logging.getLogger(__name__)

    def __init__(self, ids=(), **kwargs):
        self.unknown = self.UNKNOWN
        self.attributes = self.ATTRS
        self.logger.info("Starting load %s", self.ATTRS)
        self.out = self.load(ids, self.attributes)
        self.logger.info("Stop loading %s", self.ATTRS)

    @staticmethod
    def load(ids, attributes):
        return {i: [] for i in ids}

    def __getitem__(self, item):
        return self.out.get(item, self.unknown)


class ReportObjectCaps(ReportDictionary):
    """
    Report caps for MO
    Query: db.noc.sa.objectcapabilities.aggregate([{$unwind: "$caps"},
    {$match: {"caps.source" : "caps"}},
    {$project: {key: "$caps.capability", value: "$caps.value"} },
    {$group: {"_id": "$_id", "cap": {$push: { item: "$key", quantity: "$value" } }}}])
    """
    ATTRS = dict([("c_%s" % str(key), value) for key, value in
                  Capability.objects.filter().scalar("id", "name")])
    UNKNOWN = [""] * len(ATTRS)

    def load(self, mo_ids, attributes):
        # Namedtuple caps, for save
        Caps = namedtuple("Caps", attributes.keys())
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
                r = dict(("c_%s" % str(l["item"]), l["val"]) for l in v["cap"] if "c_%s" % str(l["item"]) in attributes)
                d[v["_id"]] = Caps(**r)
            i += 10000
        return d


class ReportObjectDetailLinks(ReportDictionary):
    """Report for MO links detail"""

    UNKNOWN = []
    ATTRS = ["Links"]

    @staticmethod
    def load(ids, attributes):
        match = {"int.managed_object": {"$in": ids}}
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
        return self.out[item] if item in self.out else {}


class ReportContainer(ReportDictionary):
    """Report for MO Container"""
    UNKNOWN = {}

    @staticmethod
    def load(ids, attributes):
        match = {"data.management.managed_object": {"$exists": True}}
        if ids:
            match = {"data.management.managed_object": {"$in": ids}}
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


class ReportObjectLinkCount(ReportDictionary):
    """Report for MO link count"""
    UNKNOWN = 0

    @staticmethod
    def load(ids, attributes):
        value = get_db()["noc.links"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$unwind": "$interfaces"},
            {"$lookup": {"from": "noc.interfaces", "localField": "interfaces", "foreignField": "_id", "as": "int"}},
            {"$group": {"_id": "$int.managed_object", "count": {"$sum": 1}}}
        ])

        return dict((v["_id"][0], v["count"]) for v in value if v["_id"])


class ReportObjectIfacesTypeStat(ReportDictionary):
    """Report for MO interfaces count"""

    UNKNOWN = 0

    @staticmethod
    def load(ids, attributes):
        i_type = "physical"
        match = {"type": i_type}
        if ids:
            match = {"type": i_type,
                     "managed_object": {"$in": ids}}
        value = get_db()["noc.interfaces"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$match": match},
            {"$group": {"_id": "$managed_object", "count": {"$sum": 1}}}
        ])

        return dict((v["_id"], v["count"]) for v in value)


class ReportObjectIfacesStatusStat(ReportDictionary):
    """Report for interfaces speed and status count"""

    # ["1G_UP", "1G_DOWN"]
    ATTRS = list("-")
    UNKNOWN = [""] * len(ATTRS)

    @staticmethod
    def load(ids, attributes):
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

        oper = True
        group = {"in_speed": "$in_speed",
                 "managed_object": "$managed_object"}
        if oper:
            group["oper_status"] = "$oper_status"

        match = {"type": "physical"}
        if ids:
            match = {"type": "physical",
                     "managed_object": {"$in": ids}}
        value = get_db()["noc.interfaces"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$match": match},
            {"$group": {"_id": group,
                        "count": {"$sum": 1}}}
        ])
        r = defaultdict(lambda: [""] * len(attributes))
        for v in value:
            c = {
                True: "Up",
                False: "Down",
                None: "-"
            }[v["_id"].get("oper_status", None)] if oper else ""

            if v["_id"].get("in_speed", None):
                c += "/" + humanize_speed(v["_id"]["in_speed"])
            else:
                c += "/-"
            # r[v["_id"]["managed_object"]].append((c, v["count"]))
            if c in attributes:
                r[v["_id"]["managed_object"]][attributes.index(c)] = v["count"]
        return r
        # return dict((v["_id"]["managed_object"], v["count"]) for v in value["result"])


class ReportObjectAttributes(ReportDictionary):

    UNKNOWN = ["", ""]

    @staticmethod
    def load(ids, attributes):
        """
        :param ids:
        :return: Dict tuple MO attributes mo_id -> (attrs_list)
        :rtype: dict
        """
        mo_attrs = {}
        attr_list = ["Serial Number", "HW version"]
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


class ReportAttrResolver(ReportDictionary):

    UNKNOWN = ["", "", "", ""]
    ATTRS = ["profile", "vendor", "version", "platform"]

    @staticmethod
    def load(ids, attributes):
        """
        :param ids:
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


class ReportObjectsHostname(ReportDictionary):
    """MO hostname"""

    UNKNOWN = None

    def __init__(self, mo_ids=(), use_facts=False):
        self.load = self.load_discovery
        super(ReportObjectsHostname).__init__(mo_ids)
        if use_facts:
            self.out.update(self.load_facts(mo_ids))

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
