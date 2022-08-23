# ----------------------------------------------------------------------
# Managed Object Discovery Stats Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any

# Third-party modules
import pandas as pd
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.main.models.pool import Pool
from noc.core.mongo.connection import get_db
from pymongo.read_preferences import ReadPreference

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


class ManagedObjectConfigDS(BaseDataSource):
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
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields)]
        return pd.DataFrame.from_records(data, index=["pool", "profile"])

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        # unmanaged_mos = ManagedObject.objects.filter(is_managed=False)
        icoll = Interface._get_collection()
        metrics = {}
        for row in icoll.aggregate(MOS_METRICS_PIPELINE):
            metrics[row["_id"]] = row["metrics"]
        for pool in Pool.objects.filter():
            for mop in ManagedObjectProfile.objects.filter():
                r = {
                    "pool": pool.name,
                    "profile": mop.name,
                    "discovered_managed_object_box": 0,
                    "discovered_managed_object_periodic": 0,
                    "discovered_interface": 0,
                    "discovered_links": 0,
                    "discovered_metrics": 0,
                }
                mos = list(
                    ManagedObject.objects.filter(
                        is_managed=True, object_profile=mop, pool=pool
                    ).values_list("id", flat=True)
                )
                if mop.enable_periodic_discovery:
                    r["discovered_managed_object_periodic"] = len(mos)
                if mop.enable_box_discovery:
                    r["discovered_managed_object_box"] = len(mos)
                # r["discovered_interface"] = Interface.objects.filter(managed_object__in=mos).count()
                # r["discovered_links"] = Link.objects.filter(linked_objects__in=mos).count()
                if mop.report_ping_rtt:
                    r["discovered_metrics"] += 1
                if mop.report_ping_attempts:
                    r["discovered_metrics"] += 1
                if mop.enable_periodic_discovery and mop.enable_periodic_discovery_metrics:
                    r["discovered_metrics"] = len(mop.metrics) * len(mos)
                    for mo_id in mos:
                        if mo_id in metrics:
                            r["discovered_metrics"] += metrics[mo_id]
                yield r
