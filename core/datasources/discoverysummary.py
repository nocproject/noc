# ----------------------------------------------------------------------
# Managed Object Discovery Stats Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# Third-party modules
from noc.inv.models.interface import Interface
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.main.models.pool import Pool
from noc.inv.models.link import Link

# NOC modules
from .base import FieldInfo, BaseDataSource

MOS_METRICS_PIPELINE = [
    {"$match": {"type": "physical"}},
    {
        "$lookup": {
            "from": "noc.interface_profiles",
            "localField": "profile",
            "foreignField": "_id",
            "as": "profile",
        }
    },
    {
        "$project": {
            "profile": {"$arrayElemAt": ["$profile", 0]},
            "managed_object": "$managed_object",
        }
    },
    {"$match": {"profile.metrics": {"$exists": True}}},
    {
        "$project": {
            "x": {"$size": "$profile.metrics"},
            "managed_object": "$managed_object",
        }
    },
    {"$group": {"_id": "$managed_object", "metrics": {"$sum": "$x"}}},
]


class DiscoverySummaryDS(BaseDataSource):
    name = "discoverysummary"

    fields = [
        FieldInfo(name="pool", type="str"),
        FieldInfo(name="profile", type="str"),
        FieldInfo(name="discovered_managed_object_box", type="int"),
        FieldInfo(name="discovered_managed_object_periodic", type="int"),
        FieldInfo(name="discovered_interface", type="int"),
        FieldInfo(name="discovered_links", type="int"),
        FieldInfo(name="discovered_metrics", type="int"),
        # FieldInfo(name="Discovered Managed Object (Box)", type="int"),
        # FieldInfo(name="Discovered Managed Object (Box)", type="int"),
        # FieldInfo(name="Discovered Interface", type="int"),
        # FieldInfo(name="Discovered Links", type="int"),
        # FieldInfo(name="Discovered Sensors", type="int"),
        # FieldInfo(name="Discovered Metrics", type="int"),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        # unmanaged_mos = ManagedObject.objects.filter(is_managed=False)
        icoll = Interface._get_collection()
        metrics = {}
        for row in icoll.aggregate(MOS_METRICS_PIPELINE):
            metrics[row["_id"]] = row["metrics"]
        row_num = 0
        for pool in Pool.objects.filter():
            for mop in ManagedObjectProfile.objects.filter():
                row_num += 1
                r = {
                    "pool": pool.name,
                    "profile": mop.name,
                    "discovered_managed_object_box": 0,
                    "discovered_managed_object_periodic": 0,
                    "discovered_interface": 0,
                    "discovered_links": 0,
                    "discovered_metrics": 0,
                }
                mos = set(
                    ManagedObject.objects.filter(
                        is_managed=True, object_profile=mop, pool=pool
                    ).values_list("id", flat=True)
                )
                if mop.enable_periodic_discovery:
                    r["discovered_managed_object_periodic"] = len(mos)
                if mop.enable_box_discovery:
                    r["discovered_managed_object_box"] = len(mos)
                r["discovered_managed_object_all"] = len(mos)
                # if mos:
                #     #     # r["discovered_interface"] = Interface.objects.filter(managed_object__in=mos).count()
                #     r["discovered_links"] = Link.objects.filter(linked_objects__in=mos).count()
                if mop.report_ping_rtt:
                    r["discovered_metrics"] += 1
                if mop.report_ping_attempts:
                    r["discovered_metrics"] += 1
                if mop.enable_periodic_discovery and mop.enable_periodic_discovery_metrics:
                    r["discovered_metrics"] = len(mop.metrics) * len(mos)
                    for mo_id in mos.intersection(set(metrics)):
                        r["discovered_metrics"] += metrics[mo_id]
                yield row_num, "pool", pool.name
                yield row_num, "profile", mop.name
                yield row_num, "discovered_managed_object_box", r["discovered_managed_object_box"]
                yield row_num, "discovered_managed_object_periodic", r[
                    "discovered_managed_object_periodic"
                ]
                yield row_num, "discovered_managed_object_all", r["discovered_managed_object_all"]
                yield row_num, "discovered_interface", r["discovered_links"]
                yield row_num, "discovered_links", r["discovered_links"]
                yield row_num, "discovered_metrics", r["discovered_metrics"]
                yield row_num, "discovered_managed_object_box_per_second", (
                    float(len(mos)) / mop.box_discovery_interval
                ) if mop.enable_box_discovery else 0
                yield row_num, "discovered_managed_object_periodic_per_second", (
                    float(len(mos)) / mop.periodic_discovery_interval
                ) if mop.enable_periodic_discovery else 0
