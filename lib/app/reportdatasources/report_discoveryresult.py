# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectDiscoveryResult datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import namedtuple
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from .base import BaseReportStream
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.lib.nosql import get_db


class ReportDiscoveryResult(BaseReportStream):
    """Report for MO links detail"""
    """
    "profile" : { "" : "Cannot fetch snmp data, check device for SNMP access"}
    "profile" : { "" : "Not find profile for OID: 1.3.6.1.4.1.6527.1.6.3 or HTTP string: " }
    "version" : { "" : "Remote error code 10005" }
    "id" : { "" : "Remote error code None, message: RPC call failed: Failed: Already reading" }
    "id" : { "" : "Remote error code None, message: RPC call failed: Failed: object of type 'NoneType' has no len()" }
    "interface" : { "" : "Remote error code None, message: RPC call failed: Failed: 'oper_status'" }
    "stp" : { "" : "Remote error code None, message: RPC call failed: Failed: Stream is closed" }
    "config" : { "" : "Remote error code None, message: RPC call failed: Failed: Already reading"
    "uptime" : { "" : "Remote error code None, message: RPC call failed: Failed: " }
    "interfacestatus" : { "" : "Remote error code 1" }
    "nri_portmap" : { "" : "Unhandled exception: list index out of range" }
    """
    builtin_sorted = True
    multiple_stream = True
    COLL_NAME = "noc.schedules.discovery.%s"
    # POOLS = [Pool.get_by_id(p) for p in set(mos.values_list("pool", flat=True))]

    @staticmethod
    def pipeline(filter_ids, match=None):
        """
        Generate pipeline for request
        :param filter_ids:
        :type filter_ids: list
        :param match: Match filter
        :type match: dict
        :return:
        :rtype: list
        """
        pipeline = [
            {"$match": {"key": {"$in": filter_ids},
                        "jcls": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"}},
            {"$project": {
                "j_id": {"$concat": ["discovery-", "$jcls", "-", {"$substr": ["$key", 0, -1]}]},
                "st": True,
                "key": True}},
            {"$lookup": {"from": "noc.joblog", "localField": "j_id", "foreignField": "_id", "as": "job"}},
            {"$project": {"job.problems": True, "st": True, "key": True}}]
            # {"$sort": {"_id": 1}}]
        if match:
            # @todo check match
            pipeline += [{"$match": match}]
        else:
            pipeline += [{"$match": {"job.problems": {"$exists": True, "$ne": {}}}}]
        return pipeline

    def extract(self):
        r = {}
        ids = set(self.sync_ids[:])

        for p in Pool.objects.filter():
            pool_ids = ids.intersection(set(ManagedObject.objects.filter(
                pool=p, is_managed=True).values_list("id", flat=True)))
            if not pool_ids:
                continue
            r[p.name] = self.convert2(get_db()[self.COLL_NAME % p.name].with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate(
                self.pipeline(list(pool_ids))))
            ids.difference_update(pool_ids)
            if not ids:
                break
        return r.values()

    @staticmethod
    def convert(**kwargs):
        Disco_problem = namedtuple("DResult", ["profile", "suggest_cli", "suggest_snmp",
                                               "version", "caps", "interface", "id",
                                               "config", "lldp", "lacp", "stp", "uptime"])
        # @todo Append info for MO
        yield {int(kwargs["key"]): kwargs["problems"]}
        # r[int(v["key"])]["time"] = v["st"]
        #       r[int(v["key"])]["problems"] = v["job"][0]["problems"]

    @staticmethod
    def convert2(yy):
        DP = namedtuple("DResult", ["profile", "suggest_cli", "suggest_snmp",
                                    "version", "caps", "interface", "id",
                                    "config", "lldp", "lacp", "stp", "huawei_ndp",
                                    "mac", "uptime"])
        DP.__new__.__defaults__ = ("",) * len(DP._fields)
        for x in yy:
            yield int(x["key"]), DP(**x["job"][0].get("problems"))
