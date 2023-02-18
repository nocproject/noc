# ----------------------------------------------------------------------
# Discovery ID Cache Poison Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, BaseDataSource
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
        FieldInfo(name="managed_object", type="int"),
        FieldInfo(name="name", type="str"),
        FieldInfo(name="address", type="str"),
        FieldInfo(name="profile", type="str"),
        FieldInfo(name="pool", type="pool"),
        FieldInfo(name="is_managed", type="bool"),
        FieldInfo(name="reason", type="str"),
        FieldInfo(name="macs", type="str"),
        FieldInfo(name="on_blacklist", type="bool"),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
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
                    "name", "address", "profile", "pool", "is_managed"
                )
            ]
            if len(data) > 0:
                if data[0]["address"] == data[1]["address"]:
                    reason = _("Duplicate MO")
                elif not data[0]["is_managed"] == data[1]["is_managed"]:
                    reason = _("MO is move")
            if reason == "Other" and MACBlacklist.is_banned_mac(row["macs"][0], is_duplicated=True):
                on_blacklist = True
            for mo in data:
                row_num += 1
                yield row_num, "managed_object", row["_id"]
                yield row_num, "name", mo["name"]
                yield row_num, "address", mo["address"]
                yield row_num, "pool", Pool.get_by_id(mo["pool"]).name
                yield row_num, "profile", Profile.get_by_id(mo["profile"]).name
                yield row_num, "mac", MAC(row["macs"][0])
                yield row_num, "reason", reason
                yield row_num, "is_managed", "True" if mo["address"] else "False"
                yield row_num, "on_blacklist", on_blacklist
