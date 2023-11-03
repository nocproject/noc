# ----------------------------------------------------------------------
# Managed Object Discovery Problem DataSource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.core.mongo.connection import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from .base import FieldInfo, FieldType, BaseDataSource


class ManagedObjectDPDS(BaseDataSource):
    name = "managedobjectdpds"
    row_index = "managed_object_id"

    safe_output = False  # Convert output object to string
    COLL_NAME = "noc.schedules.discovery.%s"
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

    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
    ] + [FieldInfo(name=f"dp.{fn}") for fn in ATTRS]

    @staticmethod
    def pipeline(filter_ids):
        """
        Generate pipeline for request
        :param filter_ids:
        :type filter_ids: list
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
            {"$match": {"job.problems": {"$exists": True, "$ne": {}}}},
        ]
        return pipeline

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        num = 1
        for p in Pool.objects.all():
            pool_ids = list(ManagedObject.objects.filter(pool=p).values_list("id", flat=True))
            if not pool_ids:
                continue
            discoveries = (
                get_db()[cls.COLL_NAME % p.name]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(cls.pipeline(pool_ids))
            )
            for d in discoveries:
                yield num, "managed_object_id", int(d["key"])
                r = d["job"][0].get("problems")
                for xx in cls.ATTRS:
                    if xx in r:
                        value = r[xx].get("", str(r[xx]) if cls.safe_output else r[xx])
                    else:
                        value = ""
                    yield num, f"dp.{xx}", value
                num += 1
