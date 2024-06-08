# ----------------------------------------------------------------------
# Managed Object Discovery Stats Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable
from collections import defaultdict

# Third-party modules
from django.db.models.aggregates import Count
from django.contrib.postgres.aggregates.general import ArrayAgg

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.core.wf.diagnostic import DiagnosticState
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


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

MOS_IFACE_PIPELINE = [
    {"$match": {"type": "physical"}},
    {"$group": {"_id": {"mo": "$managed_object", "p": "$profile"}, "metrics": {"$sum": 1}}},
]


class DiscoverySummaryDS(BaseDataSource):
    name = "discoverysummary"

    fields = [
        FieldInfo(name="pool"),
        FieldInfo(name="profile"),
        FieldInfo(name="discovered_managed_object_box", type=FieldType.UINT),
        FieldInfo(name="discovered_managed_object_periodic", type=FieldType.UINT),
        FieldInfo(name="discovered_managed_object_metrics", type=FieldType.UINT),
        FieldInfo(name="discovered_managed_object_all", type=FieldType.UINT),
        FieldInfo(name="discovered_managed_object_box_per_second", type=FieldType.FLOAT),
        FieldInfo(name="discovered_managed_object_periodic_per_second", type=FieldType.FLOAT),
        FieldInfo(name="discovered_interface", type=FieldType.UINT),
        FieldInfo(name="discovered_links", type=FieldType.UINT),
        FieldInfo(name="discovered_metrics", type=FieldType.UINT),
        # FieldInfo(name="Discovered Interface", type="int"),
        # FieldInfo(name="Discovered Links", type="int"),
        # FieldInfo(name="Discovered Sensors", type="int"),
        # FieldInfo(name="Discovered Metrics", type="int"),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        # Interface metrics
        p_metrics = {p.id: len(p.metrics) for p in InterfaceProfile.objects.filter()}
        icoll = Interface._get_collection()
        metrics = defaultdict(int)
        for row in icoll.aggregate(MOS_IFACE_PIPELINE, allowDiskUse=True):
            mo_id, i_profile = row["_id"]["mo"], row["_id"]["p"]
            metrics[mo_id] += row["metrics"] * p_metrics[i_profile]
        # Main loop
        for row_num, row in enumerate(
            ManagedObject.objects.filter(
                diagnostics__SA__state=DiagnosticState.enabled.value,
            )
            .values("pool", "object_profile")
            .annotate(dcount=Count("*"), mos=ArrayAgg("id")),
            start=1,
        ):
            mop = ManagedObjectProfile.get_by_id(row["object_profile"])
            mos_count = row["dcount"]
            mos = set(row["mos"])
            r = {
                "pool": row["pool"],
                "profile": mop.name,
                "discovered_managed_object_box": 0,
                "discovered_managed_object_periodic": 0,
                "discovered_managed_object_metrics": 0,
                "discovered_interface": 0,
                "discovered_links": 0,
                "discovered_metrics": 0,
            }
            if mop.enable_periodic_discovery:
                r["discovered_managed_object_periodic"] = mos_count
            if mop.enable_box_discovery:
                r["discovered_managed_object_box"] = mos_count
            r["discovered_managed_object_all"] = mos_count
            if mop.report_ping_rtt:
                r["discovered_metrics"] += 1
            if mop.report_ping_attempts:
                r["discovered_metrics"] += 1
            if mop.enable_metrics:
                r["discovered_managed_object_metrics"] = mos_count
                r["discovered_metrics"] = len(mop.metrics) * mos_count
                # for mo_id in mos.intersection(set(metrics)):
                r["discovered_metrics"] = sum(
                    metrics[mo_id] for mo_id in mos.intersection(set(metrics))
                )
            yield row_num, "pool", r["pool"]
            yield row_num, "profile", mop.name
            yield row_num, "discovered_managed_object_box", r["discovered_managed_object_box"]
            yield row_num, "discovered_managed_object_periodic", r[
                "discovered_managed_object_periodic"
            ]
            yield row_num, "discovered_managed_object_metrics", r[
                "discovered_managed_object_metrics"
            ]
            yield row_num, "discovered_managed_object_all", r["discovered_managed_object_all"]
            yield row_num, "discovered_interface", r["discovered_links"]
            yield row_num, "discovered_links", r["discovered_links"]
            yield row_num, "discovered_metrics", r["discovered_metrics"]
            yield row_num, "discovered_managed_object_box_per_second", (
                (float(mos_count) / mop.box_discovery_interval) if mop.enable_box_discovery else 0
            )
            yield row_num, "discovered_managed_object_periodic_per_second", (
                (float(mos_count) / mop.periodic_discovery_interval)
                if mop.enable_periodic_discovery
                else 0
            )
