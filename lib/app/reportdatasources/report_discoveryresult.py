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
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from .base import BaseReportColumn


class ReportDiscoveryResult(BaseReportColumn):
    """Report for MO links detail"""

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
            {"$lookup": {"from": "noc.joblog", "localField": "j_id",
                         "foreignField": "_id", "as": "job"}},
            {"$project": {"job.problems": True,
                          "st": True, "key": True}}]  # {"$sort": {"_id": 1}}] Not use...
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
            r[p.name] = self.convert(get_db()[self.COLL_NAME % p.name].with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED
            ).aggregate(self.pipeline(list(pool_ids))))
            ids.difference_update(pool_ids)
            if not ids:
                break
        return r.values()

    @staticmethod
    def convert(val):
        dresult = namedtuple("DResult", ["profile", "suggest_cli", "suggest_snmp",
                                         "version", "caps", "interface", "id",
                                         "config", "lldp", "lacp", "stp", "huawei_ndp",
                                         "mac", "uptime"])
        dresult.__new__.__defaults__ = ("",) * len(dresult._fields)
        for x in val:
            yield int(x["key"]), dresult(**x["job"][0].get("problems"))
