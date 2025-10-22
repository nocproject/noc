# ----------------------------------------------------------------------
# ReportObjectDiscoveryResult datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.core.mongo.connection import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from .base import BaseReportColumn


class ReportDiscoveryResult(BaseReportColumn):
    """Report for MO links detail"""

    builtin_sorted = True
    safe_output = False  # Convert outpur object to string
    COLL_NAME = "noc.schedules.discovery.%s"
    # @todo from managedobjectprofile
    ATTRS = [
        "profile",
        "suggest_cli",
        "suggest_snmp",
        "version",
        "caps",
        "interface",
        "id",
        "asset",
        "cpe",
        "vlan",
        "vpn",
        "config",
        "configvalidation",
        "lldp",
        "lacp",
        "stp",
        "huawei_ndp",
        "cdp",
        "bfd",
        "oam",
        "udld",
        "ifdesc",
        "mac",
        "xmac",
        "uptime",
        "segmentation",
        "interfacestatus",
        "prefix",
        "address",
        "metrics",
        "cpestatus",
        "nri",
        "nri_portmap",
        "nri_service",
        "hk",
        "sla",
    ]
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
            {
                "$match": {
                    "key": {"$in": filter_ids},
                    "jcls": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                }
            },
            {
                "$project": {
                    "j_id": {"$concat": ["discovery-", "$jcls", "-", {"$substr": ["$key", 0, -1]}]},
                    "st": True,
                    "key": True,
                }
            },
            {
                "$lookup": {
                    "from": "noc.joblog",
                    "localField": "j_id",
                    "foreignField": "_id",
                    "as": "job",
                }
            },
            {"$project": {"job.problems": True, "st": True, "key": True}},
        ]  # {"$sort": {"_id": 1}}] Not use...
        if match:
            # @todo check match
            pipeline += [{"$match": match}]
        else:
            pipeline += [{"$match": {"job.problems": {"$exists": True, "$ne": {}}}}]
        return pipeline

    def extract(self):
        r = {}
        ids = set(self.sync_ids[:])
        pid = {}
        for p in Pool.objects.filter():
            pool_ids = ids.intersection(
                set(ManagedObject.objects.filter(pool=p).values_list("id", flat=True))
            )
            if not pool_ids:
                continue
            pid.update(dict.fromkeys(pool_ids, p.name))
            r[p.name] = self.convert(
                get_db()[self.COLL_NAME % p.name]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(self.pipeline(list(pool_ids)))
            )
            ids.difference_update(pool_ids)
            if not ids:
                break
        for i in self.sync_ids:
            yield next(r[pid[i]], (i, ("",) * len(self.ATTRS)))
        # return list(r.values())

    def convert(self, val):
        dresult = namedtuple("DResult", self.ATTRS)
        dresult.__new__.__defaults__ = ("",) * len(dresult._fields)
        for x in val:
            r = x["job"][0].get("problems")
            yield (
                int(x["key"]),
                dresult(
                    **{xx: r[xx].get("", str(r[xx]) if self.safe_output else r[xx]) for xx in r}
                ),
            )
