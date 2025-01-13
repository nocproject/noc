# ----------------------------------------------------------------------
# Discovery ID Cache Poison Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, FieldType, ParamInfo, BaseDataSource
from noc.inv.models.discoveryid import DiscoveryID
from noc.core.mac import MAC
from noc.inv.models.macblacklist import MACBlacklist
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.main.models.pool import Pool
from noc.core.translation import ugettext as _


class DiscoveryIDCachePoisonDS(BaseDataSource):
    name = "discoveryidcachepoisonds"

    fields = [
        FieldInfo(name="managed_object", type=FieldType.UINT),
        FieldInfo(name="name"),
        FieldInfo(name="address"),
        FieldInfo(name="profile"),
        FieldInfo(name="pool"),
        FieldInfo(name="is_managed", type=FieldType.BOOL),
        FieldInfo(name="reason"),
        FieldInfo(name="mac"),
        FieldInfo(name="on_blacklist", type=FieldType.BOOL),
    ]

    params = [
        ParamInfo(name="pool", type="str", model="main.Pool"),
        ParamInfo(name="filter_dup_macs", type="bool", default=False),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        filter_dup_macs=False,
        pool: Optional[Pool] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        # Find object with equal ID
        find = DiscoveryID._get_collection().aggregate(
            [
                {"$unwind": "$macs"},
                {"$group": {"_id": "$macs", "count": {"$sum": 1}, "mo": {"$push": "$object"}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$group": {"_id": "$mo", "macs": {"$push": "$_id"}}},
            ],
            allowDiskUse=True,
        )
        row_num = 0
        for row in find:
            if not row["_id"]:
                # Empty DiscoveryID
                continue
            reason, on_blacklist = "Other", False
            data = [
                mo
                for mo in ManagedObject.objects.filter(id__in=row["_id"]).values(
                    "id", "name", "address", "profile", "pool", "is_managed"
                )
            ]
            if len(data) > 0:
                if data[0]["address"] == data[1]["address"]:
                    reason = _("Duplicate MO")
                elif not data[0]["is_managed"] == data[1]["is_managed"]:
                    reason = _("MO is move")
            if reason == "Other" and MACBlacklist.is_banned_mac(row["macs"][0], is_duplicated=True):
                on_blacklist = True
            if filter_dup_macs and on_blacklist:
                continue
            if pool and data and str(pool.id) != data[0]["pool"]:
                continue
            for mo in data:
                row_num += 1
                yield row_num, "managed_object", mo["id"]
                yield row_num, "name", mo["name"]
                yield row_num, "address", mo["address"]
                yield row_num, "pool", Pool.get_by_id(mo["pool"]).name
                yield row_num, "profile", Profile.get_by_id(mo["profile"]).name
                yield row_num, "mac", str(MAC(row["macs"][0]))
                yield row_num, "reason", reason
                yield row_num, "is_managed", mo["is_managed"]
                yield row_num, "on_blacklist", on_blacklist
