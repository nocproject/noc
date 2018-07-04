# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectDiscoveryResult datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import defaultdict
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from .base import BaseReportDataSource
from noc.main.models.pool import Pool
from noc.sa.models.objectstatus import ObjectStatus
from noc.lib.nosql import get_db


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
        pipeline = [
            {"$match": {"key": {"$in": self.mo_ids},
                        "jcls": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"}},
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
